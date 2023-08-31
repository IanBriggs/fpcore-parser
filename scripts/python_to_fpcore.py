#!/usr/bin/env python3

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
#  ____  _  _  ____  _  _   __   __ _       ____  __
# (  _ \( \/ )(_  _)/ )( \ /  \ (  ( \     (_  _)/  \
#  ) __/ )  /   )(  ) __ ((  O )/    / ____  )( (  O )
# (__)  (__/   (__) \_)(_/ \__/ \_)__)(____)(__) \__/
#              ____  ____   ___  __  ____  ____     ____  _  _
#             (  __)(  _ \ / __)/  \(  _ \(  __)   (  _ \( \/ )
#        ____  ) _)  ) __/( (__(  O ))   / ) _)  _  ) __/ )  /
#       (____)(__)  (__)   \___)\__/(__\_)(____)(_)(__)  (__/
#
# Low effort python -> fpcore conversion
#
# Notes:
# * this script should either output the correct translation or crash
#

import argparse
import os.path as path
import sys

SCR_DIR = path.abspath(path.dirname(__file__))
GIT_DIR = path.split(SCR_DIR)[0]
SRC_DIR = path.join(GIT_DIR, "src")
sys.path.append(SRC_DIR)

import ast
import os

import fpcore

from utils import Logger, Timer

logger = Logger(Logger.MEDIUM, color=Logger.blue)
timer = Timer()


FILE_EXTENSION = ".py"


def parse_arguments(argv):
    desc = "Tries to turn python defs into fpcores"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("input",
                        nargs="+",
                        help="Files, or directories to search within")
    parser.add_argument("-v", "--verbosity",
                        nargs="?",
                        default="low",
                        const="medium",
                        choices=list(Logger.CONSTANT_DICT),
                        help="Set output verbosity")
    parser.add_argument("-l", "--log-file",
                        nargs="?",
                        type=str,
                        help="Redirect logging to given file.")
    args = parser.parse_args(argv[1:])

    Logger.set_log_level(Logger.str_to_level(args.verbosity))

    if args.log_file is not None:
        Logger.set_log_filename(args.log_file)

    logger.dlog("Settings:")
    logger.dlog("      input: {}", args.input)
    logger.dlog("  verbosity: {}", args.verbosity)
    logger.dlog("   log-file: {}", args.log_file)

    return args


def constant_to_fpcore_ast(const):
    logger("Converting constant: '{}'", const)
    match const:
        case int():
            return fpcore.base_ast.Decnum(str(const))
        case float():
            return fpcore.base_ast.Decnum(str(const))
        case _:
            raise NotImplementedError(f"Unhandled constant: '{const}'")


def binop_to_fpcore_op(binop):
    match binop:
        case ast.Add():
            return "+"
        case ast.Sub():
            return "-"
        case ast.Mult():
            return "*"
        case ast.Div():
            return "/"
        case ast.Mod():
            return "fmod"
        case ast.Pow():
            return "pow"
        case _:
            raise NotImplementedError(f"{type(binop)} not implemented")


def unop_to_fpcore_op(unop):
    match unop:
        case ast.UAdd():
            return "+"
        case ast.USub():
            return "-"
        case ast.Not():
            return "not"
        case _:
            raise NotImplementedError(f"{type(unop)} not implemented")


def node_to_fpcore_ast(node):
    logger("Converting node: '{}'", node)
    match node:
        case [inner_node]:
            return node_to_fpcore_ast(inner_node)
        case ast.Return():
            return node_to_fpcore_ast(node.value)
        case ast.BinOp():
            op = binop_to_fpcore_op(node.op)
            left = node_to_fpcore_ast(node.left)
            right = node_to_fpcore_ast(node.right)
            return fpcore.base_ast.Operation(op, left, right)
        case ast.UnaryOp():
            op = unop_to_fpcore_op(node.op)
            arg = node_to_fpcore_ast(node.operand)
            return fpcore.base_ast.Operation(op, arg)
        case ast.Constant():
            return constant_to_fpcore_ast(node.value)
        case ast.Name():
            return fpcore.base_ast.Variable(node.id)
        case ast.Call():
            if not isinstance(node.func, ast.Name):
                raise NotImplementedError(
                    f"Unhandled call type: '{ast.dump(node.func)}'")
            name = node.func.id
            args = (node_to_fpcore_ast(a) for a in node.args)
            return fpcore.base_ast.Operation(name, *args)
        case _:
            raise NotImplementedError(f"Unhandled node: '{node}'")


def process_file(filename):
    assert os.path.isfile(filename), filename

    with open(filename, "r") as f:
        text = f.read()

    python_ast = ast.parse(text)

    fpcores = list()

    for node in python_ast.body:
        logger("Input node: {}", node)
        if not isinstance(node, ast.FunctionDef):
            logger.warning("Skipping unhandled node: '{}'", node)
            continue
        name = node.name
        args = [fpcore.base_ast.Variable(item.arg) for item in node.args.args]
        body = node_to_fpcore_ast(node.body)
        fpc = fpcore.base_ast.FPCore(name, args, list(), body)
        fpcores.append(fpc)

    return fpcores


def process_input(name):
    filenames = list()
    if os.path.isfile(name):
        if not name.endswith(FILE_EXTENSION):
            logger.warning("Splitting non '{}' file: {}", FILE_EXTENSION, name)
        filenames.append(name)
    elif os.path.isdir(name):
        for root, dirs, files in os.walk(name):
            for file in files:
                if file.endswith(FILE_EXTENSION):
                    full = os.path.join(root, file)
                    filenames.append(full)
    else:
        logger.error("cannot access '{}': No such file or directory", name)

    fpcores = list()
    for filename in filenames:
        fpcores += process_file(filename)

    return fpcores


def main(argv):
    args = parse_arguments(argv)

    fpcores = list()
    for name in args.input:
        fpcores += process_input(name)

    for fpc in fpcores:
        print(fpc)

    return 0


if __name__ == "__main__":
    timer.start()

    try:
        return_code = main(sys.argv)
    except KeyboardInterrupt:
        print("")
        print("Goodbye")
        return_code = 130  # meaning "Script terminated by Control-C"

    timer.stop()

    logger("Elapsed time: {:4f} sec", timer.elapsed_time())

    sys.exit(return_code)
