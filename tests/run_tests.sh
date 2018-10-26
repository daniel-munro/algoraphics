#!/bin/sh

SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
cd "$SCRIPTPATH"

TESTS=$(ls *.py)

for TEST in $TESTS
do
    printf "$TEST\n"
    python3 $TEST
done
