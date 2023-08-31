#!/usr/bin/env bash

# Echo commands and exit on error
set -x
set -e

# The location of this file
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set current dir in case the script was ran from somewhere else
cd "${SCRIPT_DIR}"

# Purge, clone, then clean non-fpcore files
rm -rf FPBench
git clone https://github.com/FPBench/FPBench.git
find FPBench -type f ! -name "*.fpcore" -delete
find FPBench -type d -empty -delete

# Ditto
rm -rf herbie
git clone https://github.com/herbie-fp/herbie.git
find herbie -type f ! -name "*.fpcore" -delete
find herbie -type d -empty -delete
