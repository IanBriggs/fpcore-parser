#!/usr/bin/env python3

import json
import argparse
import os
import os.path as path
from pprint import pprint
import sys


def parse_arguments(argv):
    desc = "Convert Herbie's web query JSON logs to FPCore"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("filenames",
                        nargs="+",
                        help="JSON files to convert")
    args = parser.parse_args(argv[1:])

    filenames = list()
    for dn in args.filenames:
        if os.path.isfile(dn) and dn.endswith(".json"):
            filenames.append(dn)
        else:
            filenames.extend([path.join(dn, fn)
                           for fn in os.listdir(dn)
                           if fn.endswith(".json")])

    filenames.sort()
    args.filenames = filenames

    return args


def read_herbie_json(filename):
    basename = path.split(filename)[1].rstrip(".json")

    with open(filename, 'r') as f:
        data = json.load(f)

    inputs = list()
    for i, test in enumerate(data["tests"]):
        # Some do not have "vars" populated,
        # give a decent try to add one letter variables
        if test["vars"] == False:
            test["vars"] = list()
            for c in list("abcdefghijklmnopqrstuvwxyz"):
                if f" {c} " in test["input"] or f" {c})" in test["input"]:
                    test["vars"].append(c)
        # Skip inputs that use reserved words as variables
        keywords = {
            "FPCore", "if", "let", "let*", "while", "while*", "for", "for*",
            "tensor", "tensor*", "cast", "array", "digits",
            "E", "LOG2E", "LOG10E", "LN2", "LN10",
            "PI", "PI_2", "PI_4", "M_1_PI", "M_2_PI",
            "M_2_SQRTPI", "SQRT2", "SQRT1_2", "INFINITY", "NAN",
            "TRUE", "FALSE",
            "+", "-", "*", "/", "fabs",
            "fma", "exp", "exp2", "expm1", "log",
            "log10", "log2", "log1p", "pow", "sqrt",
            "cbrt", "hypot", "sin", "cos", "tan",
            "asin", "acos", "atan", "atan2", "sinh",
            "cosh", "tanh", "asinh", "acosh", "atanh",
            "erf", "erfc", "tgamma", "lgamma", "ceil",
            "floor", "fmod", "remainder", "fmax", "fmin",
            "fdim", "copysign", "trunc", "round", "nearbyint",
            "<", ">", "<=", ">=", "==",
            "!=", "and", "or", "not", "isfinite",
            "isinf", "isnan", "isnormal", "signbit",
            "dim", "size", "ref",
            "expt",
        }
        if any([key in test["vars"] for key in keywords]):
            print("Dropping input:")
            pprint(test)
            print("")
            continue
        args = " ".join(test["vars"])

        # Some inputs don't list keywords as variables,
        # but still use them as variables
        body = test["input"].replace('"', '').replace("expt", "pow")
        known_bad = {
            "(* sqrt",
            "sqrt)",
            "(* sin",
        }
        if any([kb in body for kb in known_bad]):
            print("Dropping input:")
            pprint(test)
            print()
            continue

        # Build the FPCore
        digits = len(str(len(inputs)))
        lines = [
            f"(FPCore ({args})",
            f"    :description \"herbie web query\"",
            f"    :name \"set_{basename}_number_{i:0{digits}}\"",
        ]
        if ("pre" in test and test["pre"] != "TRUE"
                and (not test["pre"].startswith("(< if"))):
            pre = test["pre"].replace('"', '')
            lines.append(f"    :pre {pre}")
        lines.append(f"    {body})")
        inputs.append("\n".join(lines))

    return inputs


def main(argv):
    args = parse_arguments(argv)

    for filename in args.filenames:
        inputs = read_herbie_json(filename)
        basename = path.split(filename)[1].rstrip(".json")
        with open(basename + ".fpcore", 'w') as f:
            for input in inputs:
                f.write(input + "\n\n")

    return 0


if __name__ == "__main__":
    try:
        return_code = main(sys.argv)
    except KeyboardInterrupt:
        print("")
        print("Goodbye")
        return_code = 130  # meaning "Script terminated by Control-C"

    sys.exit(return_code)
