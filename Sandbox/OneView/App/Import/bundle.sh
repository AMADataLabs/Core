#!/bin/bash

files=$(find . -name lambda_function.py)
directories=${files//\/lambda_function.py/}

for directory in $directories; do
    name=$(echo $directory | sed 's/..*\///')
    zip -j $name.zip $directory/lambda_function.py
done
