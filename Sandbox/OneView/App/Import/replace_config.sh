#!/bin/bash

files=$(find . -name lambda_function.py)
echo $files

for file in $files; do
    cp $file $file.old
    awk -f replace_config.awk $file.old > $file
done
