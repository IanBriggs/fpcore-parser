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
#  __    ____  _  _  ____  ____     ____  _  _
# (  )  (  __)( \/ )(  __)(  _ \   (  _ \( \/ )
# / (_/\ ) _)  )  (  ) _)  )   / _  ) __/ )  /
# \____/(____)(_/\_)(____)(__\_)(_)(__)  (__/
#
# The lexer
#
# Notes:
# * the order of lexer token definitions is purposeful since sly does priority
#   based on order in the file (e.g. HEXNUM must come before DECNUM)
# * changes from what is given on the FPBench website are noted with the word
#   "Modification"
# * `pylance` freaks out since sly messes with the python ast, disable with the
#   next line
# pyright: reportUndefinedVariable=false
#

import sys

from sly import Lexer
from utils import Logger, Timer

logger = Logger(level=Logger.EXTRA, color=Logger.blue)
timer = Timer()

# As FPCores are parsed named ones are added to this dict.
# This means user's can call functions, but only after defining them
ADDED_OPERATIONS = dict()


class FPCoreLexError(Exception):
    def __init__(self, msg, tok):
        self.msg = msg
        self.tok = tok


class FPCoreLexer(Lexer):
    tokens = {
        # Delimiters
        LP, # left parenthesis
        RP, # right parenthesis
        LB, # left square bracket
        RB, # right square bracket
        COLON,
        BANG,
        HASH, # Modification: hash is short for setting precision to integer

        # Literals
        RATIONAL,
        HEXNUM,
        DECNUM,
        STRING,

        # Symbols
        SYMBOL,

        # Keywords
        FPCORE,
        IF,
        LET,
        LET_STAR,
        WHILE,
        WHILE_STAR,
        FOR,
        FOR_STAR,
        TENSOR,
        TENSOR_STAR,
        CAST,
        ARRAY,
        DIGITS,

        # Constants
        CONSTANT,

        # Operations
        OPERATION,
    }

    # Ignored input
    @_(r"\n+")
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')
    ignore_space = r"\s"
    ignore_comment = r"\;.*"

    LP = r"\("
    RP = r"\)"
    LB = r"\["
    RB = r"\]"
    COLON = r":"
    HASH = r"#"

    # From https://fpbench.org/spec/fpcore-2.0.html#g:rational
    # This regex allows leading zeros for both numerator and denominator
    RATIONAL = (
        r"[+-]?"             # an optional plus (+) or minus (-) sign
        r"[0-9]+"            # any sequence of decimal digits
        r"/"                 # a slash
        r"[0-9]*[1-9][0-9]*" # a nonzero sequence of decimal digits
    )

    # From https://fpbench.org/spec/fpcore-2.0.html#g:hexnum
    #     Modification: to be used in a case sensitive environment
    HEXNUM = (
        r"[+-]?"             # an optional plus (+) or minus (-) sign
        r"0[xX]"             # 0x or 0X
        r"("                 # followed by either
        r"[0-9a-fA-F]+"      #     hexadecimal digits
        r"(\.[0-9a-fA-F]+)?" #     optional period and more hexadecimal digits
        r"|"                 #   or
        r"\.[0-9a-fA-F]+)"   #     period and hexadecimal digits
        r"("                 # followed by optional
        r"[pP]"              #     p or P
        r"[-+]?"             #     an optional plus (+) or minus (-) sign
        r"[0-9]+)?"          #     decimal digits
    )

    # From https://fpbench.org/spec/fpcore-2.0.html#g:decnum
    #     Modification: to be used in a case sensitive environment
    DECNUM = (
        r"[-+]?"       # an optional plus (+) or minus (-) sign
        r"("           # followed by either
        r"[0-9]+"      #     decimal digits
        r"(\.[0-9]+)?" #     optional period and more decimal digits
        r"|"           #   or
        r"\.[0-9]+)"   #     period and decimal digits
        r"("           # followed by optional
        r"[eE]"        #     e or E
        r"[-+]?"       #     an optional plus (+) or minus (-) sign
        r"[0-9]+)?"    #     decimal digits
    )

    # From https://fpbench.org/spec/fpcore-2.0.html#g:string
    #   Modification: added general whitespace to catch newlines
    #   Modification: added α-ωΑ-Ω
    #   Modification: added ×
    @_(r'"([\sα-ωΑ-Ω×\x20-\x21\x23-\x5b\x5d-\x7e]|\\["\\])*"')
    def STRING(self, t):
        self.lineno += t.value.count('\n')
        return t

    # From https://fpbench.org/spec/fpcore-2.0.html#g:symbol
    #   Modification: added α-ωΑ-Ω
    SYMBOL = (
        r"[α-ωΑ-Ωa-zA-Z~!@$%^&*_\-+=<>.?/:]"     # non-digit
        r"[α-ωΑ-Ωa-zA-Z0-9~!@$%^&*_\-+=<>.?/:]*" # zero or more of any
    )

    # Since SYMBOL matches all keywords we need to do token remapping.

    SYMBOL["FPCore"] = FPCORE
    FPCORE = "FPCore"

    SYMBOL["if"] = IF
    IF = "if"

    SYMBOL["let"] = LET
    LET = "let"

    SYMBOL["let*"] = LET_STAR
    LET_STAR = "let*"

    SYMBOL["while"] = WHILE
    WHILE = "while"

    SYMBOL["while*"] = WHILE_STAR
    WHILE_STAR = "while*"

    SYMBOL["for"] = FOR
    FOR = "for"

    SYMBOL["for*"] = FOR_STAR
    FOR_STAR = "for*"

    SYMBOL["tensor"] = TENSOR
    TENSOR = "tensor"

    SYMBOL["tensor*"] = TENSOR_STAR
    TENSOR_STAR = "tensor*"

    SYMBOL["cast"] = CAST
    CAST = "cast"

    SYMBOL["array"] = ARRAY
    ARRAY = "array"

    SYMBOL["digits"] = DIGITS
    DIGITS = "digits"

    CONSTANTS = sorted([
        # Supported Mathematical Constants
        "E", "LOG2E", "LOG10E", "LN2", "LN10",
        "PI", "PI_2", "PI_4", "M_1_PI", "M_2_PI",
        "M_2_SQRTPI", "SQRT2", "SQRT1_2", "INFINITY", "NAN",
        # Supported Boolean Constants
        "TRUE", "FALSE",
    ], key=len)
    # Access is done through index instead of iterating over the array contents
    # since doing the latter will not actually get the value we want set due to
    # how SLY gets the value.
    for i in range(len(CONSTANTS)):
        SYMBOL[CONSTANTS[i]] = CONSTANT
    CONSTANT = "({})".format(")|(".join(CONSTANTS))

    OPERATIONS = sorted([
        # Supported Mathematical Operations
        "+", "-", "*", "/", "fabs",
        "fma", "exp", "exp2", "expm1", "log",
        "log10", "log2", "log1p", "pow", "sqrt",
        "cbrt", "hypot", "sin", "cos", "tan",
        "asin", "acos", "atan", "atan2", "sinh",
        "cosh", "tanh", "asinh", "acosh", "atanh",
        "erf", "erfc", "tgamma", "lgamma", "ceil",
        "floor", "fmod", "remainder", "fmax", "fmin",
        "fdim", "copysign", "trunc", "round", "nearbyint",
        # Supported Testing Operations
        "<", ">", "<=", ">=", "==",
        "!=", "and", "or", "not", "isfinite",
        "isinf", "isnan", "isnormal", "signbit",
        # Supported Tensor Operations
        "dim", "size", "ref",
    ], key=len)
    for i in range(len(OPERATIONS)):
        SYMBOL[OPERATIONS[i]] = OPERATION
    _not_regex = "({})".format(")|(".join(OPERATIONS))
    OPERATION = _not_regex.replace("+", "\\+").replace("*", "\\*")

    # At the end so '!=' gets precedence over '!'
    SYMBOL[r"!"] = BANG
    BANG = r"!"

    def error(self, t):
        msg = "Line {}: Bad character '{}'".format(self.lineno, t.value[0])
        raise FPCoreLexError(msg, t)


_lexer = FPCoreLexer()


def lex(text):
    """Tokenize input text as FPCore"""
    try:
        timer.start()
        lexed = _lexer.tokenize(text)
    finally:
        timer.stop()
    return lexed


def main(argv):
    logger.set_log_level(Logger.EXTRA)

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

    logger.blog("Input text", numbered)

    for token in lex(text):
        logger("{:14} '{}'", token.type, token.value)

    logger("Lexing time: {:.6f} ms", timer.elapsed_time() * 1000)


if __name__ == "__main__":
    try:
        return_code = main(sys.argv)
    except KeyboardInterrupt:
        print("")
        print("Goodbye")
        return_code = 130 # meaning "Script terminated by Control-C"

    sys.exit(return_code)
