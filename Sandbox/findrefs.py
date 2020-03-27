#!/bin/bash

common_code_files=$(/bin/ls -1 CommonCode | sed 's/\.py$//')
common_model_code_files=$(/bin/ls -1 CommonModelCode | sed 's/\.py$//')
script_files=$(find . -name "*.py" | sed 's/ /#/g')
# notebook_files=$(find . -name "*.ipynb" | sed 's/ /#/g')
notebook_files=''
all_code_files=$(echo ${script_files}$'\n'${notebook_files} | cat)
common_code_output_raw='refs_common_code_raw.csv'
common_code_output='refs_common_code.csv'
common_model_code_output_raw='refs_common_model_code_raw.csv'
common_model_code_output='refs_common_model_code.csv'

rm -f $common_code_output_raw
rm -f $common_model_code_output_raw

for code_file in $all_code_files; do
  code_file=$(echo $code_file | sed 's/#/ /g')
  echo "Processing file $code_file"

  for common_code_file in $common_code_files; do
    fgrep -H "from $common_code_file" "$code_file" >> $common_code_output_raw
  done

  for common_code_file in $common_model_code_files; do
    fgrep -H "from $common_code_file" "$code_file" >> $common_model_code_output_raw
  done
done

echo '"File","Module"' > $common_code_output
cat $common_code_output_raw | sed -e 's/ *"\?from \([^ ][^ ]*\).*/\1/' -e 's/\([^:][^:]*\):\(..*\)/"\1","\2"/' >> $common_code_output

echo '"File","Module"' > $common_model_code_output
cat $common_model_code_output_raw | sed -e 's/ *"\?from \([^ ][^ ]*\).*/\1/' -e 's/\([^:][^:]*\):\(..*\)/"\1","\2"/' >> $common_model_code_output

rm -f $common_code_output_raw
rm -f $common_model_code_output_raw
