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
#  ____   __   ____  ____  ____         __   __ _  ____
# (  _ \ / _\ (  _ \/ ___)(  __)       / _\ (  ( \(    \
#  ) __//    \ )   /\___ \ ) _)  ____ /    \/    / ) D (
# (__)  \_/\_/(__\_)(____/(____)(____)\_/\_/\_)__)(____/
#              ____  ____  __  __ _  ____    ____  _  _
#             (  _ \(  _ \(  )(  ( \(_  _)  (  _ \( \/ )
#        ____  ) __/ )   / )( /    /  )(  _  ) __/ )  /
#       (____)(__)  (__\_)(__)\_)__) (__)(_)(__)  (__/
#
# Example usage of the FPCore Parser
#
# Notes:
# * first it sets up python's search path
#   + as such, sorting the imports will break the script
#

import os.path as path
import sys

SCR_DIR = path.abspath(path.dirname(__file__))
GIT_DIR = path.split(SCR_DIR)[0]
SRC_DIR = path.join(GIT_DIR, "src")
sys.path.append(SRC_DIR)

import argparse
import fpcore
import os
from fpcore.base_ast import *

from utils import Logger, Timer


logger = Logger(Logger.MEDIUM, color=Logger.blue)
timer = Timer()


def parse_arguments(argv):
    desc = "Parse and print FPCore"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("input",
                        nargs="?",
                        help="Files to convert")
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


def main(argv):
    args = parse_arguments(argv)

    # If input is unset then read from stdin
    if args.input is None:
        text = sys.stdin.read()
    else:
        with open(args.input, "r") as f:
            text = f.read()

    fpcores = fpcore.parse(text)

    # Convert to string uses python's stack, so increase the size
    sys.setrecursionlimit(100_000)

    for fpc in fpcores:
        fpc_str = str(fpc)
        print("input -> parse -> str:")
        print("  ", fpc_str)
        print()

        fpc_repr = repr(fpc)
        print("input -> parse -> repr:")
        print("  ", fpc_repr)
        print()

        try:
            re_fpc_str = str(eval(fpc_repr))
        except SyntaxError as e:
            if e.msg == "too many nested parentheses":
                print("Too many nested parentheses for python's eval!\n\n")
                continue
            else:
                raise e

        if fpc_str != re_fpc_str:
            print("input -> parse -> repr -> eval -> str:")
            print("  ", re_fpc_str)
            print()
            print("MISMATCH!")
            return (1)

        print("\n\n")

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
