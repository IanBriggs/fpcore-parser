#  ____  ____   ___  __  ____  ____    ____   __   ____  ____  ____  ____
# (  __)(  _ \ / __)/  \(  _ \(  __)  (  _ \ / _\ (  _ \/ ___)(  __)(  _ \
#  ) _)  ) __/( (__(  O ))   / ) _)    ) __//    \ )   /\___ \ ) _)  )   /
# (__)  (__)   \___)\__/(__\_)(____)  (__)  \_/\_/(__\_)(____/(____)(__\_)
#
# An attempt at an FPCore 2.0 compliant parser in python.
#
# Relevant information can be found at
# [FPBench's website](https://fpbench.org/spec/fpcore-2.0.html)
#
#
#  ____   __   ____  ____  ____  ____     ____  _  _
# (  _ \ / _\ (  _ \/ ___)(  __)(  _ \   (  _ \( \/ )
#  ) __//    \ )   /\___ \ ) _)  )   / _  ) __/ )  /
# (__)  \_/\_/(__\_)(____/(____)(__\_)(_)(__)  (__/
#
# The parser
#
# Notes:
# * to get the CNF you can run `grep "# cnf" parser.py | sed "s|.*# cnf||g"`
# * the spec doesn't clearly differentiate between lexer tokens and parse rules
#   everything looks like parse rules, so more specificity is presented here
#    + in CNF strings:
#      - angle brackets indicate use of a rule
#      - curly brackets indicate use of a lexer token
#    + in SLY strings:
#      - lower case indicates use of a rule
#      - upper case indicates lexer token
#      - some tokens are from just literals and so the tokens are used
# * changes from what is given on the FPBench website are noted with the word
#   "Modification"
# * `pylance` freaks out since sly messes with the python ast, disable this
#   with the next line
# pyright: reportUndefinedVariable=false
#

import sys

from sly import Parser

import fpcore.base_ast as base_ast
import fpcore.lexer as fpcore_lexer
from utils import Timer

timer = Timer()


class FPCoreParseError(Exception):
    """Raised when parsing fails"""

    def __init__(self, msg, p=None):
        self.msg = msg
        self.p = p


class FPCoreParser(Parser):
    tokens = fpcore_lexer.FPCoreLexer.tokens | {"ADDED_OPERATION"}

    # Modification: add <fpcores> to allow multiple fpcore items
    # cfn fpcores :=
    # cfn     | <fpcore>+
    @_("fpcore { fpcore }")
    def fpcores(self, p):
        return (p.fpcore0, *p.fpcore1)

    # Modification: split out <signature>
    # cfn fpcore :=
    # cfn     | ( FPCore <signature> <property>* <expr> )
    @_("LP FPCORE signature { property } expr RP")
    def fpcore(self, p):
        name = p.signature[0]
        args = p.signature[1]
        prop = {k: v for k, v in p.property}
        fpc = base_ast.FPCore(name, args, prop, p.expr)
        # Add operation here now that there is a body for the FPCore
        if name is not None:
            fpcore_lexer.ADDED_OPERATIONS[name] = fpc
        return fpc

    # cfn signature :=
    # cfn      | {symbol}? (<argument>*)
    @_("[ SYMBOL ] LP { argument } RP")
    def signature(self, p):
        name = p[0][0]
        args = p.argument
        return (name, args)

    # cfn dimension :=
    # cfn     | <variable>
    # cfn     | <number>
    @_("variable",
       "number")
    def dimension(self, p):
        return p[0]

    # cfn argument :=
    # cfn     | <variable>
    @_("variable")
    def argument(self, p):
        return p[0]

    # cfn     | ( <variable> <dimension>+ )
    @_("LP variable dimension { dimension } RP")
    def argument(self, p):
        return p.variable.set_dimension((p.dimension0, *p.dimension1))

    # cfn     | ( ! <property>* <variable> <dimension>* )
    @_("LP BANG { property } variable { dimension } RP")
    def argument(self, p):
        if len(p.property) > 0:
            prop = {k: v for k, v in p.property}
            p.variable.add_properties(prop)
        if len(p.dimension) > 0:
            p.variable.set_dimension(p.dimension)
        return p.variable

    # Modification: split out many <expr> as their own rules
    # cfn expr :=
    # cfn     | <number>
    # cfn     | <variable>
    # cfn     | <operation>
    # cfn     | <if_expr>
    # cfn     | <let_expr>
    # cfn     | <while_expr>
    # cfn     | <for_expr>
    # cfn     | <tensor_expr>
    @_("number",
       "variable",
       "operation",
       "if_expr",
       "let_expr",
       "while_expr",
       "for_expr",
       "tensor_expr")
    def expr(self, p):
        return p[0]

    # cfn     | {constant}
    @_("CONSTANT")
    def expr(self, p):
        return base_ast.Constant(p[0])

    # cfn     | ( cast <expr> )
    @_("LP CAST expr RP")
    def expr(self, p):
        return base_ast.Cast(p.expr)

    # cfn     | ( array <expr>* )
    @_("LP ARRAY { expr } RP")
    def expr(self, p):
        return base_ast.Array(p.expr)

    # cfn     | ( ! <property>* <expr> )
    @_("LP BANG { property } expr RP")
    def expr(self, p):
        if len(p.property) > 0:
            prop = {k: v for k, v in p.property}
            p.expr.add_properties(prop)
        return p.expr

    # Modification: hash is short for setting precision to integer
    # cfn     | ( # <expr> )
    @_("LP HASH expr RP")
    def expr(self, p):
        p.expr.add_properties({"precision": "integer"})
        return p.expr

    # number :=
    # cfn     | {rational}
    @_("RATIONAL")
    def number(self, p):
        return base_ast.Rational(p[0])

    # cfn     | {decnum}
    @_("DECNUM")
    def number(self, p):
        return base_ast.Decnum(p[0])

    # cfn     | {hexnum}
    @_("HEXNUM")
    def number(self, p):
        return base_ast.Hexnum(p[0])

    # cfn     | ( digits {decnum} {decnum} {decnum} )
    @_("LP DIGITS DECNUM DECNUM DECNUM RP")
    def number(self, p):
        return base_ast.Digits(p[2], p[3], p[4])

    # Modification: allow {operation} in <property>
    # cfn property :=
    # cfn     | : {symbol} <data>
    # cfn     | : {operation} <data>
    @_("COLON SYMBOL data",
       "COLON OPERATION data")
    def property(self, p):
        return (p[1], p[2])

    # Modification: allow <operation> in <data>
    # Modification: allow <let_expr> in <data>
    # Modification: allow <binding> in <data>
    # Modification: allow <if_expr> in <data>
    # cfn data :=
    # cfn     | {symbol}
    # cfn     | <number>
    # cfn     | {string}
    # cfn     | <operation>
    # cfn     | <let_expr>
    # cfn     | <binding>
    # cfn     | <if_expr>
    @_("SYMBOL",
       "number",
       "STRING",
       "operation",
       "let_expr",
       "binding",
       "if_expr")
    def data(self, p):
        return p[0]

    # cfn     | ( <data>* )
    @_("LP { data } RP")
    def data(self, p):
        return p.data

    # Modification: change + to *, so zero argument operations can be used
    # Modification: add <added_operation>, so we can define and call FPCores
    #               as operations
    # cfn operation :=
    # cfn     | ( {operation} <expr>* )
    # cfn     | ( {added_operation} <expr>* )
    @_("LP OPERATION { expr } RP",
       "LP ADDED_OPERATION { expr } RP")
    def operation(self, p):
        return base_ast.Operation(p[1], *p.expr)

    # cfn if_expr :=
    # cfn     | ( if <expr> <expr> <expr> )
    @_("LP IF expr expr expr RP")
    def if_expr(self, p):
        return base_ast.If(p.expr0, p.expr1, p.expr2)

    # Modification: split out <binding>
    # cfn let_expr :=
    # cfn     | ( let ( <binding>* ) <expr> )
    @_("LP LET LP { binding } RP expr RP")
    def let_expr(self, p):
        bind = {var: expr for var, expr in p.binding}
        return base_ast.Let(bind, p.expr)

    # cfn     | ( let* ( <binding>* ) <expr> )
    @_("LP LET_STAR LP { binding } RP expr RP")
    def let_expr(self, p):
        bind = {var: expr for var, expr in p.binding}
        return base_ast.LetStar(bind, p.expr)

    # Modification: split out <update_binding>
    # cfn while_expr :=
    # cfn     | ( while <expr> ( <update_binding>* ) <expr> )
    @_("LP WHILE expr LP { update_binding } RP expr RP")
    def while_expr(self, p):
        up_bind = {var: (init, upd) for var, init, upd in p.update_binding}
        return base_ast.While(p.expr0, up_bind, p.expr1)

    # cfn     | ( while* <expr> ( <update_binding>* ) <expr> )
    @_("LP WHILE_STAR expr LP { update_binding } RP expr RP")
    def while_expr(self, p):
        up_bind = {var: (init, upd) for var, init, upd in p.update_binding}
        return base_ast.WhileStar(p.expr0, up_bind, p.expr1)

    # cfn for_expr :=
    # cfn     | ( for ( <binding>* ) ( <update_binding>* ) <expr> )
    @_("LP FOR LP { binding } RP LP { update_binding } RP expr RP")
    def for_expr(self, p):
        bind = {var: expr for var, expr in p.binding}
        up_bind = {var: (init, upd) for var, init, upd in p.update_binding}
        return base_ast.For(bind, up_bind, p.expr)

    # cfn     | ( for* ( <binding>* ) ( <update_binding>* ) <expr> )
    @_("LP FOR_STAR LP { binding } RP LP { update_binding } RP expr RP")
    def for_expr(self, p):
        bind = {var: expr for var, expr in p.binding}
        up_bind = {var: (init, upd) for var, init, upd in p.update_binding}
        return base_ast.ForStar(bind, up_bind, p.expr)

    # cfn tensor_expr :=
    # cfn     | ( tensor ( <binding>* ) <expr> )
    @_("LP TENSOR LP { binding } RP expr RP")
    def tensor_expr(self, p):
        bind = {var: expr for var, expr in p.binding}
        return base_ast.Tensor(bind, p.expr)

    # cfn     | ( tensor* ( <binding>* ) ( <update_binding>* ) <expr> )
    @_("LP TENSOR_STAR LP { binding } RP LP { update_binding } RP expr RP")
    def tensor_expr(self, p):
        bind = {var: expr for var, expr in p.binding}
        up_bind = {var: (init, upd) for var, init, upd in p.update_binding}
        return base_ast.TensorStar(bind, up_bind, p.expr)

    # cfn binding :=
    # cfn     | [ <variable> <expr> ]
    @_("LB variable expr RB")
    def binding(self, p):
        return (p.variable, p.expr)

    # cfn update_binding :=
    # cfn     | [ <variable> <expr> <expr> ]
    @_("LB variable expr expr RB")
    def update_binding(self, p):
        return (p.variable, p.expr0, p.expr1)

    # Modification: rename <symbol> to <variable>
    # cfn variable :=
    # cfn     | {symbol}
    @_("SYMBOL")
    def variable(self, p):
        return base_ast.Variable(p[0])

    # errors
    def error(self, p):
        if p is None:
            raise FPCoreParseError("Unexpected end of FPCore")

        if p.type == "SYMBOL":
            # Assume this is an added operation
            # Mark that it need to be set
            if p.value not in fpcore_lexer.ADDED_OPERATIONS:
                fpcore_lexer.ADDED_OPERATIONS[p.value] = None
            p.type = "ADDED_OPERATION"
            self.errok()
            return p

        # Using parens for let bindings is a non-FPCore thing to do
        # Putting it in the language causes some shift-reduce errors that I
        # don't want to deal with
        if (self.symstack[-2].type == "LET"
            and self.symstack[-1].type == "LP"
                and p.type == "LP"):
            fmt = "Line {}: Only use square brackets for let bindings"
            msg = fmt.format(p.lineno)
            raise FPCoreParseError(msg)

        raise FPCoreParseError("Syntax error at", p)


_parser = FPCoreParser()


def parse(text):
    """Parse input text as FPCore"""
    tokens = fpcore_lexer.lex(text)
    with timer:
        assert (len(fpcore_lexer.ADDED_OPERATIONS) == 0)
        parsed = _parser.parse(tokens)
        for op in fpcore_lexer.ADDED_OPERATIONS:
            if op is None:
                raise FPCoreParseError(f"Operation never defined: '{op}'")
        fpcore_lexer.ADDED_OPERATIONS = dict()
    return parsed


def main(argv):
    if len(argv) == 1:
        text = sys.stdin.read()
    elif len(argv) == 2:
        with open(argv[1], "r") as f:
            text = f.read()
    if text.strip() == "":
        text = "(FPCore (x) :pre (<= 1/100 x 1/2) (/ (- (exp x) 1) x))"

    lines = text.splitlines()
    max_line_num = len(lines)
    fmt = "{{:>{}}}: {{}}".format(len(str(max_line_num)))
    numbered = "\n".join(fmt.format(num+1, line) for num, line
                         in enumerate(text.splitlines()))

    print("Input text:")
    print(f"\n{numbered}\n")

    for fpc in parse(text):
        print("repr:")
        print(f"\n{repr(fpc)}\n")
        print("str:")
        print(f"\n{str(fpc)}\n")

    lexing_time = fpcore_lexer.timer.elapsed_time_ms()
    print(" Lexing time: {:.6f} ms".format(lexing_time))
    print("Parsing time: {:.6f} ms".format(timer.elapsed_time_ms()))


if __name__ == "__main__":
    try:
        return_code = main(sys.argv)
    except KeyboardInterrupt:
        print("")
        print("Goodbye")
        return_code = 130  # meaning "Script terminated by Control-C"

    sys.exit(return_code)
