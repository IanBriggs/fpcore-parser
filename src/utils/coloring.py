#   ___  __   __     __  ____  __  __ _   ___     ____  _  _
#  / __)/  \ (  )   /  \(  _ \(  )(  ( \ / __)   (  _ \( \/ )
# ( (__(  O )/ (_/\(  O ))   / )( /    /( (_ \ _  ) __/ )  /
#  \___)\__/ \____/ \__/(__\_)(__)\_)__) \___/(_)(__)  (__/
#
# A simple ANSI text colorizer
#

from __future__ import annotations
from collections.abc import Callable
import re


FOREGROUND_COLOR_CODES = {
    "black": 30,
    "red": 31,
    "green": 32,
    "yellow": 33,
    "blue": 34,
    "magenta": 35,
    "cyan": 36,
    "white": 37,
}


def color_to_number(name: str,
                    background: bool = False,
                    bright: bool = False) -> int:
    name = name.strip().lower()
    try:
        # To go from a foreground color code to a background color code add 10
        # To go from a color to a bright color add 60
        # These can be combined
        return (FOREGROUND_COLOR_CODES[name]
                + 10 * background
                + 60 * bright)
    except KeyError:
        raise ValueError(f"Invalid color: '{name}'")


def make_colorizer(name: str,
                   background: bool = False,
                   bright: bool = False) -> Callable[[str], str]:
    num = color_to_number(name, background, bright)
    fmt = f"\x1b[{num}m{{}}\x1b[0m"
    return lambda text: fmt.format(text)


# To get a regular expression for these color codes we could make a clever re
# that will most likely include more patterns than we want, or we could just
# `or` the 33 patterns we can produce.
numbers = [0]  # for the reset number
for name in FOREGROUND_COLOR_CODES:
    for background in [False, True]:
        for bright in [False, True]:
            numbers.append(color_to_number(name, background, bright))
patterns = [r"\x1b\[" + f"{num}m" for num in numbers]
re_str = "(" + ")|(".join(patterns) + ")"
ANSI_COLOR_RE = re.compile(re_str)


def strip_color(text: str) -> str:
    return ANSI_COLOR_RE.sub("", text)

def 

black = make_colorizer("black")
red = make_colorizer("red")
green = make_colorizer("green")
yellow = make_colorizer("yellow")
blue = make_colorizer("blue")
magenta = make_colorizer("magenta")
cyan = make_colorizer("cyan")
white = make_colorizer("white")

bg_black = make_colorizer("black", background=True)
bg_red = make_colorizer("red", background=True)
bg_green = make_colorizer("green", background=True)
bg_yellow = make_colorizer("yellow", background=True)
bg_blue = make_colorizer("blue", background=True)
bg_magenta = make_colorizer("magenta", background=True)
bg_cyan = make_colorizer("cyan", background=True)
bg_white = make_colorizer("white", background=True)

bright_black = make_colorizer("black", bright=True)
bright_red = make_colorizer("red", bright=True)
bright_green = make_colorizer("green", bright=True)
bright_yellow = make_colorizer("yellow", bright=True)
bright_blue = make_colorizer("blue", bright=True)
bright_magenta = make_colorizer("magenta", bright=True)
bright_cyan = make_colorizer("cyan", bright=True)
bright_white = make_colorizer("white", bright=True)

bg_bright_black = make_colorizer("black", background=True, bright=True)
bg_bright_red = make_colorizer("red", background=True, bright=True)
bg_bright_green = make_colorizer("green", background=True, bright=True)
bg_bright_yellow = make_colorizer("yellow", background=True, bright=True)
bg_bright_blue = make_colorizer("blue", background=True, bright=True)
bg_bright_magenta = make_colorizer("magenta", background=True, bright=True)
bg_bright_cyan = make_colorizer("cyan", background=True, bright=True)
bg_bright_white = make_colorizer("white", background=True, bright=True)


def main(argv) -> int:
    lines = [
        black("black"),
        red("red"),
        green("green"),
        yellow("yellow"),
        blue("blue"),
        magenta("magenta"),
        cyan("cyan"),
        white("white"),
        bright_black("bright_black"),
        bright_red("bright_red"),
        bright_green("bright_green"),
        bright_yellow("bright_yellow"),
        bright_blue("bright_blue"),
        bright_magenta("bright_magenta"),
        bright_cyan("bright_cyan"),
        bright_white("bright_white"),
        bg_black("bg_black"),
        bg_red("bg_red"),
        bg_green("bg_green"),
        bg_yellow("bg_yellow"),
        bg_blue("bg_blue"),
        bg_magenta("bg_magenta"),
        bg_cyan("bg_cyan"),
        bg_white("bg_white"),
        bg_bright_black("bg_bright_black"),
        bg_bright_red("bg_bright_red"),
        bg_bright_green("bg_bright_green"),
        bg_bright_yellow("bg_bright_yellow"),
        bg_bright_blue("bg_bright_blue"),
        bg_bright_magenta("bg_bright_magenta"),
        bg_bright_cyan("bg_bright_cyan"),
        bg_bright_white("bg_bright_white"),
    ]
    colors = "\n".join(lines)

    print("Colors!")
    print(colors)
    print()
    print("No more colors!")
    print(strip_color(colors))

    return 0


if __name__ == "__main__":
    import sys

    try:
        return_code = main(sys.argv)
    except KeyboardInterrupt:
        print("")
        print("Goodbye")
        return_code = 130  # meaning "Script terminated by Control-C"

    sys.exit(return_code)
