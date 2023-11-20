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
#  ____  ____   ___  __  ____  ____    _
# (  __)(  _ \ / __)/  \(  _ \(  __)  / )
#  ) _)  ) __/( (__(  O ))   / ) _)  / /
# (__)  (__)   \___)\__/(__\_)(____)(_/
#                    __  __ _  __  ____                ____  _  _
#                   (  )(  ( \(  )(_  _)              (  _ \( \/ )
#        ____  ____  )( /    / )(   )(  ____  ____  _  ) __/ )  /
#       (____)(____)(__)\_)__)(__) (__)(____)(____)(_)(__)  (__/
#

from .lexer import FPCoreLexError
from .parser import FPCoreParseError, parse
from . import base_ast

from .ast_methods import (
    dunder_repr,
    dunder_str,
    dunder_math_operations,
    pretty_str,
    eval,
    extract_name,
)