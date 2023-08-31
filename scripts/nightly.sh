#!/usr/bin/env bash

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
#  __ _  __  ___  _  _  ____  __    _  _   ____  _  _
# (  ( \(  )/ __)/ )( \(_  _)(  )  ( \/ ) / ___)/ )( \
# /    / )(( (_ \) __ (  )(  / (_/\ )  /_ \___ \) __ (
# \_)__)(__)\___/\_)(_/ (__) \____/(__/(_)(____/\_)(_/
#
# Test script
#

set -e

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPTS_DIR}"
cd ..
GIT_DIR="$(pwd)"

export PYTHONPATH="${GIT_DIR}/src"

for f in $(find benchmarks -name "*.fpcore" | sort); do
    echo $f
    python3 ${SCRIPTS_DIR}/parse_and_repr.py $f
    echo -e "\n\n\n\n\n"
done
