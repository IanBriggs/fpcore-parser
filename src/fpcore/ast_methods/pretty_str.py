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
#  ____  _  _  __ _  ____  ____  ____
# (    \/ )( \(  ( \(    \(  __)(  _ \
#  ) D () \/ (/    / ) D ( ) _)  )   /
# (____/\____/\_)__)(____/(____)(__\_)
#            ____  ____  ____     ____  _  _
#           / ___)(_  _)(  _ \   (  _ \( \/ )
#      ____ \___ \  )(   )   / _  ) __/ )  /
#     (____)(____/ (__) (__\_)(_)(__)  (__/
#
# String conversion
#

from fpcore.base_ast import (Array, ASTNode, Atom, Cast, Digits, Expr, For,
                             ForStar, FPCore, If, Let, LetStar, Operation,
                             Tensor, TensorStar, Variable, While, WhileStar)
from utils import add_method


def binding_str(bindings: dict) -> str:
    return " ".join([f"[{k} {v}]" for k, v in bindings.items()])


def update_binding_str(update_bindings: dict) -> str:
    return " ".join([f"[{k} {i} {u}]" for k, (i, u)
                     in update_bindings.items()])


def properties_str(expr: Expr, inner: str) -> str:
    if len(expr.properties) == 0:
        return inner
    prop = " ".join([f":{sym} {data}" for sym, data
                     in expr.properties.items()])
    return f"(! {prop} {inner})"


@add_method(ASTNode)
def pretty_str(self: ASTNode) -> str:
    # Make sure calling pretty_str leads to an error if not overridden
    class_name = type(self).__name__
    msg = "pretty_str not implemented for class {}".format(class_name)
    raise NotImplementedError(msg)


@add_method(Atom)
def pretty_str(self: Atom) -> str:
    return properties_str(self, self.source)


@add_method(Variable)
def pretty_str(self: Variable) -> str:
    inner = self.source
    if self.dimension is not None:
        dim = " ".join([str(d) for d in self.dimension])
        inner = "({} {})".format(self.source, dim)
    return properties_str(self, inner)


@add_method(Digits)
def pretty_str(self: Digits) -> str:
    inner = "(digits {} {} {})".format(self.mantissa,
                                       self.exponent,
                                       self.base)
    return properties_str(self, inner)


@add_method(Operation)
def pretty_str(self: Operation) -> str:
    args = " ".join([str(a) for a in self.args])
    inner = "({} {})".format(self.op, args)
    return properties_str(self, inner)


@add_method(If)
def pretty_str(self: If) -> str:
    inner = "(if {} {} {})".format(self.cond, self.true, self.false)
    return properties_str(self, inner)


@add_method(Let)
def pretty_str(self: Let) -> str:
    bind = binding_str(self.bindings)
    inner = "(let ({}) {})".format(bind, self.body)
    return properties_str(self, inner)


@add_method(LetStar)
def pretty_str(self: LetStar) -> str:
    bind = binding_str(self.bindings)
    inner = "(let* ({}) {})".format(bind, self.body)
    return properties_str(self, inner)


@add_method(While)
def pretty_str(self: While) -> str:
    update_bind = update_binding_str(self.update_bindings)
    inner = "(while {} ({}) {})".format(self.cond,
                                        update_bind,
                                        self.body)
    return properties_str(self, inner)


@add_method(WhileStar)
def pretty_str(self: WhileStar) -> str:
    update_bind = update_binding_str(self.update_bindings)
    inner = "(while* {} ({}) {})".format(self.cond,
                                         update_bind,
                                         self.body)
    return properties_str(self, inner)


@add_method(For)
def pretty_str(self: For) -> str:
    bind = binding_str(self.bindings)
    update_bind = update_binding_str(self.update_bindings)
    inner = "(for ({}) ({}) {})".format(bind,
                                        update_bind,
                                        self.body)
    return properties_str(self, inner)


@add_method(ForStar)
def pretty_str(self: ForStar) -> str:
    bind = binding_str(self.bindings)
    update_bind = update_binding_str(self.update_bindings)
    inner = "(for* ({}) ({}) {})".format(bind,
                                         update_bind,
                                         self.body)
    return properties_str(self, inner)


@add_method(Tensor)
def pretty_str(self: Tensor) -> str:
    bind = binding_str(self.bindings)
    inner = "(tensor ({}) {})".format(bind,
                                      self.body)
    return properties_str(self, inner)


@add_method(TensorStar)
def pretty_str(self: TensorStar) -> str:
    bind = binding_str(self.bindings)
    update_bind = update_binding_str(self.update_bindings)
    inner = "(tensor* ({}) ({}) {})".format(bind,
                                            update_bind,
                                            self.body)
    return properties_str(self, inner)


@add_method(Cast)
def pretty_str(self: Cast) -> str:
    return properties_str(self, "(cast {})".format(self.body))


@add_method(Array)
def pretty_str(self: Array) -> str:
    items_str = " ".join([str(i) for i in self.items])
    inner = "(array {})".format(items_str)
    return properties_str(self, inner)


@add_method(FPCore)
def pretty_str(self: FPCore) -> str:
    name_str = "" if self.operation_name is None else self.operation_name + " "
    arguments_str = " ".join([str(a) for a in self.arguments])
    prop = "\n        ".join([(f':{sym} "{data}"'
                             if type(data) == str
                             else f':{sym} {data}')
                              for sym, data in self.properties.items()])
    return (f"(FPCore {name_str}({arguments_str})\n"
            f"        {prop}\n"
            "\n"
            f"        {self.body})")
