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
#  ____  _  _  ____  ____   __    ___  ____
# (  __)( \/ )(_  _)(  _ \ / _\  / __)(_  _)
#  ) _)  )  (   )(   )   //    \( (__   )(
# (____)(_/\_) (__) (__\_)\_/\_/ \___) (__)
#              __ _   __   _  _  ____     ____  _  _
#             (  ( \ / _\ ( \/ )(  __)   (  _ \( \/ )
#        ____ /    //    \/ \/ \ ) _)  _  ) __/ )  /
#       (____)\_)__)\_/\_/\_)(_/(____)(_)(__)  (__/
#
# A poor example of adding an ast method, since it only applies to the top
# level FPCore
#


from fpcore.base_ast import ASTNode, FPCore
from utils import add_method


@add_method(ASTNode)
def extract_name(self, *args, **kwargs):
    # Make sure calling extract_name leads to an error if not overridden
    class_name = type(self).__name__
    msg = "extract_name not implemented for class {}".format(class_name)
    raise NotImplementedError(msg)


@add_method(FPCore)
def extract_name(self: FPCore) -> str:
    # First get the explicit FPCore name
    if self.operation_name is not None:
        return self.operation_name

    # Otherwise look in properties for a name
    name = "unnamed_fpcore"
    times_defined = 0
    for p in self.properties:
        if p.name == "name":
            name = p.value
            times_defined += 1

    # Report when there are multiple ':name's
    if times_defined > 1:
        logger.warning("':name' was defined {} time in FPCore", times_defined)
        logger.warning("Using '{}'", name)

    return name
