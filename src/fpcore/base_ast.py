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
#  ____   __   ____  ____         __   ____  ____    ____  _  _
# (  _ \ / _\ / ___)(  __)       / _\ / ___)(_  _)  (  _ \( \/ )
#  ) _ (/    \\___ \ ) _)  ____ /    \\___ \  )(  _  ) __/ )  /
# (____/\_/\_/(____/(____)(____)\_/\_/(____/ (__)(_)(__)  (__/
#
# A bare bones AST
#
# Notes:
# * it is designed to have methods defined in their own files
#

# Class Structure:
#
# ASTNode
#  ├─ Expr
#  │  ├─ Atom
#  │  │  ├─ Constant
#  │  │  ├─ Variable
#  │  │  └─ Number
#  │  │     ├─ Rational
#  │  │     ├─ Decnum
#  │  │     ├─ Hexnum
#  │  │     └─ Digits
#  │  ├─ Operation
#  │  ├─ If
#  │  ├─ Let
#  │  │  └─ LetStar
#  │  ├─ While
#  │  │  └─ WhileStar
#  │  ├─ For
#  │  │  └─ ForStar
#  │  ├─ Tensor
#  │  │  └─ TensorStar
#  │  ├─ Cast
#  │  └─ Array
#  └─ FPCore

from typing import Dict, List, Tuple


class FPCorePropertyError(Exception):
    """Raised when a property is redefined"""

    def __init__(self, msg: str):
        self.msg = msg


class ASTNode:
    def __init__(self) -> None:
        self.properties = dict()

    def add_properties(self, properties: Dict):
        # Check for redefinition but allow precision to be redefined
        defined = self.properties.keys()
        incoming = properties.keys()
        redefined = [k for k in incoming if k in defined and k != "precision"]
        if len(redefined) != 0:
            first = redefined[0]
            raise FPCorePropertyError(f"Redefined property '{first}'")
        # Add new properties
        self.properties.update(properties)
        return self


class Expr(ASTNode):
    pass


class Atom(Expr):
    def __init__(self, source: str) -> None:
        super().__init__()
        self.source = source


class Constant(Atom):
    pass


class Variable(Atom):
    def __init__(self, source: str) -> None:
        super().__init__(source)
        self.dimension = None

    def set_dimension(self, *dimension: Tuple[int, ...]):
        self.dimension = dimension
        return self


class Number(Atom):
    pass


class Rational(Number):
    pass


class Decnum(Number):
    pass


class Hexnum(Number):
    pass


class Digits(Number):
    def __init__(self, mantissa: int, exponent: int, base: int) -> None:
        super().__init__(source=f"{mantissa} {exponent} {base}")
        self.mantissa = mantissa
        self.exponent = exponent
        self.base = base


class Operation(Expr):
    def __init__(self, op: str, *args: Tuple[Expr, ...]) -> None:
        super().__init__()
        self.op = op
        self.args = args


class If(Expr):
    def __init__(self, cond: Expr, true: Expr, false: Expr) -> None:
        super().__init__()
        self.cond = cond
        self.true = true
        self.false = false


class Let(Expr):
    def __init__(self, bindings: Dict[Variable, Expr], body: Expr) -> None:
        super().__init__()
        self.bindings = bindings
        self.body = body


class LetStar(Let):
    pass


class While(Expr):
    def __init__(self,
                 cond: Expr,
                 update_bindings: Dict[Variable, Tuple[Expr, Expr]],
                 body: Expr) -> None:
        super().__init__()
        self.cond = cond
        self.update_bindings = update_bindings
        self.body = body


class WhileStar(While):
    pass


class For(Expr):
    def __init__(self,
                 bindings: Dict[Variable, Expr],
                 update_bindings: Dict[Variable, Tuple[Expr, Expr]],
                 body: Expr) -> None:
        super().__init__()
        self.bindings = bindings
        self.update_bindings = update_bindings
        self.body = body


class ForStar(For):
    pass


class Tensor(Expr):
    def __init__(self, bindings: Dict[Variable, Expr], body: Expr) -> None:
        super().__init__()
        self.bindings = bindings
        self.body = body


class TensorStar(Tensor):
    def __init__(self,
                 bindings: Dict[Variable, Expr],
                 update_bindings: Dict[Variable, Tuple[Expr, Expr]],
                 body: Expr) -> None:
        super().__init__(bindings, body)
        self.update_bindings = update_bindings


class Cast(Expr):
    def __init__(self, body: Expr) -> None:
        super().__init__()
        self.body = body


class Array(Expr):
    def __init__(self, items: list[Expr]) -> None:
        super().__init__()
        self.items = items


class FPCore(ASTNode):
    def __init__(self,
                 operation_name: str,
                 arguments: List[Variable],
                 properties: dict,
                 body: Expr) -> None:
        super().__init__()
        self.operation_name = operation_name
        self.arguments = arguments
        self.properties = properties
        self.body = body
