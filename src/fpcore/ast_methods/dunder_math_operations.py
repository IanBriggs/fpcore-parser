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
#            _  _   __  ____  _  _
#           ( \/ ) / _\(_  _)/ )( \
#      ____ / \/ \/    \ )(  ) __ (
#     (____)\_)(_/\_/\_/(__) \_)(_/
#            __  ____  ____  ____   __  ____  __  __   __ _  ____
#           /  \(  _ \(  __)(  _ \ / _\(_  _)(  )/  \ (  ( \/ ___)
#      ____(  O )) __/ ) _)  )   //    \ )(   )((  O )/    /\___ \
#     (____)\__/(__)  (____)(__\_)\_/\_/(__) (__)\__/ \_)__)(____/
#         ____  _  _
#        (  _ \( \/ )
#      _  ) __/ )  /
#     (_)(__)  (__/
#
# Magic methods to integrate FPCore with python
#

from fpcore.base_ast import ASTNode, Expr, FPCore, Number, Operation, Property
from utils import add_method, Logger

logger = Logger(level=Logger.EXTRA)


def cast_to_astnode(x):
    typ = type(x)
    if typ == FPCore:
        logger.dlog("Extracting body from FPCore: {}", x)
        x = x.body
    elif typ == int:
        x = Number(str(x))
        x.add_properties([Property("precision", "integer")])
    elif typ == float:
        x = Number(str(x))
        x.add_properties([Property("precision", "binary64")])
    elif not issubclass(typ, ASTNode):
        sx = str(x)
        try:
            float(sx)
        except ValueError:
            raise ValueError(f"Non-numeric value: {sx}")
        logger.dlog("Casting {} to Number type: {}", typ, sx)
        x = Number(sx)
    return x


def add_unary_dunder(dunder_name, fpcore_name):
    def default(self, *args, **kwargs):
        class_name = type(self).__name__
        msg = f"{dunder_name} not implemented for class '{class_name}'"
        raise NotImplementedError(msg)
    setattr(ASTNode, dunder_name, default)

    if fpcore_name == "":
        def expr(self):
            return self
    else:
        def expr(self):
            return Operation(fpcore_name, self)
    setattr(Expr, dunder_name, expr)


def add_binary_dunder(dunder_name, fpcore_name):
    def default(self, *args, **kwargs):
        class_name = type(self).__name__
        msg = f"{dunder_name} not implemented for class '{class_name}'"
        raise NotImplementedError(msg)
    setattr(ASTNode, dunder_name, default)

    def expr(self, other):
        try:
            return Operation(fpcore_name, self, cast_to_astnode(other))
        except:
            raise NotImplemented()
    setattr(Expr, dunder_name, expr)

    def rexpr(self, other):
        return Operation(fpcore_name, cast_to_astnode(other), self)
    setattr(Expr, dunder_name.replace("__", "__r", 1), rexpr)


add_unary_dunder("__pos__", "")
add_unary_dunder("__neg__", "-")
add_unary_dunder("__abs__", "fabs")
add_unary_dunder("__round__", "round")
add_unary_dunder("__floor__", "floor")
add_unary_dunder("__ceil__", "ceil")
add_unary_dunder("__trunc__", "trunc")

add_binary_dunder("__add__", "+")
add_binary_dunder("__sub__", "-")
add_binary_dunder("__mul__", "*")
add_binary_dunder("__truediv__", "/")
add_binary_dunder("__pow__", "pow")  # TODO: lacks support for math.pow

# Lack of support due to:
# https://docs.python.org/3/reference/datamodel.html
# Note that __pow__() should be defined to accept an optional third argument if
# the ternary version of the built-in pow() function is to be supported.
