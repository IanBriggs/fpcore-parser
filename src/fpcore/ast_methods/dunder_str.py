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

from fpcore.base_ast import (ASTNode, Array, Cast, Digits, Expr, Atom, FPCore,
                             For, ForStar, If, Let, LetStar, Operation, Tensor,
                             TensorStar, Variable, While, WhileStar)
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
def __str__(self: ASTNode) -> str:
    # Make sure calling __str__ leads to an error if not overridden
    class_name = type(self).__name__
    msg = "__str__ not implemented for class {}".format(class_name)
    raise NotImplementedError(msg)


@add_method(Atom)
def __str__(self: Atom) -> str:
    return properties_str(self, self.source)


@add_method(Variable)
def __str__(self: Variable) -> str:
    inner = self.source
    if self.dimension is not None:
        dim = " ".join([str(d) for d in self.dimension])
        inner = "({} {})".format(self.source, dim)
    return properties_str(self, inner)


@add_method(Digits)
def __str__(self: Digits) -> str:
    inner = "(digits {} {} {})".format(self.mantissa,
                                       self.exponent,
                                       self.base)
    return properties_str(self, inner)


@add_method(Operation)
def __str__(self: Operation) -> str:
    args = " ".join([str(a) for a in self.args])
    inner = "({} {})".format(self.op, args)
    return properties_str(self, inner)


@add_method(If)
def __str__(self: If) -> str:
    inner = "(if {} {} {})".format(self.cond, self.true, self.false)
    return properties_str(self, inner)


@add_method(Let)
def __str__(self: Let) -> str:
    bind = binding_str(self.bindings)
    inner = "(let ({}) {})".format(bind, self.body)
    return properties_str(self, inner)


@add_method(LetStar)
def __str__(self: LetStar) -> str:
    bind = binding_str(self.bindings)
    inner = "(let* ({}) {})".format(bind, self.body)
    return properties_str(self, inner)


@add_method(While)
def __str__(self: While) -> str:
    update_bind = update_binding_str(self.update_bindings)
    inner = "(while {} ({}) {})".format(self.cond,
                                        update_bind,
                                        self.body)
    return properties_str(self, inner)


@add_method(WhileStar)
def __str__(self: WhileStar) -> str:
    update_bind = update_binding_str(self.update_bindings)
    inner = "(while* {} ({}) {})".format(self.cond,
                                         update_bind,
                                         self.body)
    return properties_str(self, inner)


@add_method(For)
def __str__(self: For) -> str:
    bind = binding_str(self.bindings)
    update_bind = update_binding_str(self.update_bindings)
    inner = "(for ({}) ({}) {})".format(bind,
                                        update_bind,
                                        self.body)
    return properties_str(self, inner)


@add_method(ForStar)
def __str__(self: ForStar) -> str:
    bind = binding_str(self.bindings)
    update_bind = update_binding_str(self.update_bindings)
    inner = "(for* ({}) ({}) {})".format(bind,
                                         update_bind,
                                         self.body)
    return properties_str(self, inner)


@add_method(Tensor)
def __str__(self: Tensor) -> str:
    bind = binding_str(self.bindings)
    inner = "(tensor ({}) {})".format(bind,
                                      self.body)
    return properties_str(self, inner)


@add_method(TensorStar)
def __str__(self: TensorStar) -> str:
    bind = binding_str(self.bindings)
    update_bind = update_binding_str(self.update_bindings)
    inner = "(tensor* ({}) ({}) {})".format(bind,
                                            update_bind,
                                            self.body)
    return properties_str(self, inner)


@add_method(Cast)
def __str__(self: Cast) -> str:
    return properties_str(self, "(cast {})".format(self.body))


@add_method(Array)
def __str__(self: Array) -> str:
    items_str = " ".join([str(i) for i in self.items])
    inner = "(array {})".format(items_str)
    return properties_str(self, inner)


@add_method(FPCore)
def __str__(self: FPCore) -> str:
    name_str = "" if self.operation_name is None else self.operation_name + " "
    arguments_str = " ".join([str(a) for a in self.arguments])
    prop = " ".join([f":{sym} {data}" for sym,
                    data in self.properties.items()])
    return "(FPCore {}({}) {} {})".format(name_str,
                                          arguments_str,
                                          prop,
                                          self.body)
