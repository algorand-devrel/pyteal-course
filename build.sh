#!/usr/bin/env bash

mkdir -p ./build/
# clean
rm -f ./build/*.teal

set -e # die on error

# python ./compile.py "" ./build/approval.teal ./build/clear.teal
python ./compile.py ./build/approval.teal ./build/clear.teal
