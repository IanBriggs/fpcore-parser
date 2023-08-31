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
#  ____  _  _   __   __       ____  _  _
# (  __)/ )( \ / _\ (  )     (  _ \( \/ )
#  ) _) \ \/ //    \/ (_/\ _  ) __/ )  /
# (____) \__/ \_/\_/\____/(_)(__)  (__/
#
# Arbitrary precision evaluation
#

import mpmath
from fpcore.base_ast import (
    ASTNode, Constant, FPCore, Number, Operation, Variable)
from utils import add_method

_CONST_MAPPING = {
    "E": lambda: mpmath.e,
    "INFINITY": lambda: mpmath.inf,
    "LN10": lambda: mpmath.log(10),
    "LN2": lambda: mpmath.log(2),
    "LOG10E": lambda: mpmath.log10(mpmath.e),
    "LOG2E": lambda: mpmath.log(mpmath.e, b=2),
    "M_1_PI": lambda: 1 / mpmath.pi,
    "M_2_PI": lambda: 2 / mpmath.pi,
    "M_2_SQRTPI": lambda: 2 / mpmath.sqrt(mpmath.pi),
    "NAN": lambda: mpmath.nan,
    "PI_2": lambda: mpmath.pi / 2,
    "PI_4": lambda: mpmath.pi / 4,
    "PI": lambda: mpmath.pi,
    "SQRT1_2": lambda: 1 / mpmath.sqrt(2),
    "SQRT2": lambda: mpmath.sqrt(2),
}

_UNOP_MAPPING = {
    "-": lambda x: -x,
    "acos": lambda x: mpmath.acos(x),
    "acosh": lambda x: mpmath.acosh(x),
    "asin": lambda x: mpmath.asin(x),
    "asinh": lambda x: mpmath.asinh(x),
    "atan": lambda x: mpmath.atan(x),
    "atanh": lambda x: mpmath.atanh(x),
    "cbrt": lambda x: mpmath.cbrt(x),
    "ceil": lambda x: mpmath.ceil(x),
    "cos": lambda x: mpmath.cos(x),
    "cosh": lambda x: mpmath.cosh(x),
    "erf": lambda x: mpmath.erf(x),
    "erfc": lambda x: mpmath.erfc(x),
    "exp": lambda x: mpmath.exp(x),
    "exp2": lambda x: mpmath.power(2, x),
    "expm1": lambda x: mpmath.expm1(x),
    "fabs": lambda x: mpmath.fabs(x),
    "floor": lambda x: mpmath.floor(x),
    "lgamma": lambda x: mpmath.loggamma(x),
    "log": lambda x: mpmath.log(x),
    "log10": lambda x: mpmath.log10(x),
    "log1p": lambda x: mpmath.log1p(x),
    "log2": lambda x: mpmath.log(x, b=2),
    "sin": lambda x: mpmath.sin(x),
    "sinh": lambda x: mpmath.sinh(x),
    "sqrt": lambda x: mpmath.sqrt(x),
    "tan": lambda x: mpmath.tan(x),
    "tanh": lambda x: mpmath.tanh(x),
    "tgamma": lambda x: mpmath.gamma(x),
}

_BINOP_MAPPING = {
    "-": lambda a, b: a - b,
    "!=": lambda a, b: a != b,
    "*": lambda a, b: a * b,
    "/": lambda a, b: a / b,
    "+": lambda a, b: a + b,
    "<": lambda a, b: a < b,
    "<=": lambda a, b: a <= b,
    "==": lambda a, b: a == b,
    ">": lambda a, b: a > b,
    ">=": lambda a, b: a >= b,
    "atan2": lambda a, b: mpmath.atan2(a, b),
    "fdim": lambda a, b: max(0, a - b),
    "fmax": lambda a, b: max(a, b),
    "fmin": lambda a, b: min(a, b),
    "fmod": lambda a, b: mpmath.fmod(a, b),
    "hypot": lambda a, b: mpmath.hypot(a, b),
    "pow": lambda a, b: mpmath.power(a, b),
}


@add_method(ASTNode)
def eval(self, precision, assignment=None):
    with mpmath.workprec(precision):
        return self._eval(assignment=assignment)


@add_method(ASTNode)
def _eval(self, *args, **kwargs):
    # Make sure calling _eval leads to an error if not overridden
    class_name = type(self).__name__
    msg = "_eval not implemented for class {}".format(class_name)
    raise NotImplementedError(msg)


@add_method(Constant)
def _eval(self, assignment=None):
    try:
        return _CONST_MAPPING[self.source]()
    except KeyError:
        raise NotImplementedError(f"Unknown constant '{self.source}'")


@add_method(Variable)
def _eval(self, assignment=None):
    if assignment is not None and self.source not in assignment:
        raise NameError(f"'{self.source}' not in _evaluation environment")
    val = assignment[self.source]
    if type(val) == mpmath.mpf:
        return val
    return mpmath.mpf(val)


@add_method(Number)
def _eval(self, assignment=None):
    return mpmath.mpf(self.source)


@add_method(Operation)
def _eval(self, assignment=None):
    f_args = [arg._eval(assignment) for arg in self.args]

    if len(f_args) == 1 and self.op in _UNOP_MAPPING:
        return _UNOP_MAPPING[self.op](f_args[0])

    if len(f_args) == 2 and self.op in _BINOP_MAPPING:
        return _BINOP_MAPPING[self.op](f_args[0], f_args[1])

    msg = f"Operation not yet supported for _eval: '{self.op}'"
    raise NotImplementedError(msg)


@add_method(FPCore)
def _eval(self, assignment=None):
    # Check that arity matches
    expected = len(self.arguments)
    actual = len(assignment)
    if expected != actual:
        msg = f"FPCore expected {expected} arguments, got {actual}"
        raise TypeError(msg)

    return self.body._eval(assignment)
