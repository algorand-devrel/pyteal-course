#!/usr/bin/env bash

mkdir -p ./build/
rm -f ./build/*.teal

set -e # die on error
# source ./venv/Scripts/activate
python ./approval.py > ./build/approval.teal
python ./clear.py > ./build/clear.teal
# deactivate
