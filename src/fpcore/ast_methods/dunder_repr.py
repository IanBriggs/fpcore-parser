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
#            ____  ____  ____  ____     ____  _  _
#           (  _ \(  __)(  _ \(  _ \   (  _ \( \/ )
#      ____  )   / ) _)  ) __/ )   / _  ) __/ )  /
#     (____)(__\_)(____)(__)  (__\_)(_)(__)  (__/
#
# String conversion
#

from fpcore.base_ast import (Array, ASTNode, Atom, Cast, Digits, Expr, For,
                             FPCore, If, Let, Operation, Tensor, TensorStar,
                             Variable, While)
from utils import add_method


def binding_repr(bindings: dict) -> str:
    return ", ".join([f"{repr(k)}: {repr(v)}" for k, v in bindings.items()])


def update_binding_repr(update_bindings: dict) -> str:
    return ", ".join([f"{repr(k)}: ({repr(i)}, {repr(u)})" for k, (i, u)
                      in update_bindings.items()])


def auto_class_repr(node: ASTNode, args: str) -> str:
    class_name = type(node).__name__
    return f"{class_name}({args})"


def auto_properties_repr(expr: Expr, args: str) -> str:
    base = auto_class_repr(expr, args)
    prop_str = ""
    if len(expr.properties) != 0:
        props = [f"{repr(k)}: {repr(v)}" for k, v in expr.properties.items()]
        prop_args = "{" + ", ".join(props) + "}"
        prop_str = f".add_properties({prop_args})"
    return base + prop_str


@add_method(ASTNode)
def __repr__(self: ASTNode) -> str:
    # Make sure calling __repr__ leads to an error if not overridden
    class_name = type(self).__name__
    msg = "__repr__ not implemented for class {}".format(class_name)
    raise NotImplementedError(msg)


@add_method(Atom)
def __repr__(self: Atom) -> str:
    return auto_properties_repr(self, repr(self.source))


@add_method(Variable)
def __repr__(self: Variable) -> str:
    rep = auto_properties_repr(self, repr(self.source))
    dim_str = ""
    if self.dimension is not None:
        dim = ", ".join([str(d) for d in self.dimension])
        dim_str = f".set_dimension({dim})"
    return rep + dim_str


@add_method(Digits)
def __repr__(self: Digits) -> str:
    args = f"{self.mantissa}, {self.exponent}, {self.base}"
    return auto_properties_repr(self, args)


@ add_method(Operation)
def __repr__(self: Operation) -> str:
    op_args = ", ".join([repr(a) for a in self.args])
    args = f"{repr(self.op)}, {op_args}"
    return auto_properties_repr(self, args)


@ add_method(If)
def __repr__(self: If) -> str:
    args = f"{repr(self.cond)}, {repr(self.true)}, {repr(self.false)}"
    return auto_properties_repr(self, args)


@ add_method(Let)
def __repr__(self: Let) -> str:
    bind = binding_repr(self.bindings)
    args = f"{{{bind}}}, {repr(self.body)}"
    return auto_properties_repr(self, args)


@add_method(While)
def __repr__(self: While) -> str:
    update_bind = update_binding_repr(self.update_bindings)
    args = f"{repr(self.cond)}, {{{update_bind}}}, {repr(self.body)}"
    return auto_properties_repr(self, args)


@add_method(For)
def __repr__(self: For) -> str:
    bind = binding_repr(self.bindings)
    update_bind = update_binding_repr(self.update_bindings)
    args = f"{{{bind}}}, {{{update_bind}}}, {repr(self.body)}"
    return auto_properties_repr(self, args)


@add_method(Tensor)
def __repr__(self: Tensor) -> str:
    bind = binding_repr(self.bindings)
    args = f"{{{bind}}}, {repr(self.body)}"
    return auto_properties_repr(self, args)


@add_method(TensorStar)
def __repr__(self: TensorStar) -> str:
    bind = binding_repr(self.bindings)
    update_bind = update_binding_repr(self.update_bindings)
    args = f"{{{bind}}}, {{{update_bind}}}, {repr(self.body)}"
    return auto_properties_repr(self, args)


@add_method(Cast)
def __repr__(self: Cast) -> str:
    return auto_properties_repr(self, repr(self.body))


@add_method(Array)
def __repr__(self: Array) -> str:
    items_repr = ", ".join([repr(i) for i in self.items])
    args = f"[{items_repr}]"
    return auto_properties_repr(self, args)


@add_method(FPCore)
def __repr__(self: FPCore) -> str:
    arguments_repr = ", ".join([repr(a) for a in self.arguments])
    props = [f"{repr(k)}: {repr(v)}" for k, v in self.properties.items()]
    properties_repr = "{" + ", ".join(props) + "}"
    args = "{}, [{}], {}, {}".format(repr(self.operation_name),
                                     arguments_repr,
                                     properties_repr,
                                     repr(self.body))
    return auto_class_repr(self, args)
