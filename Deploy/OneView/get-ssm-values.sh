#!/bin/bash

export AWS_PAGER=""
OUTPUT_FILE=ssm_parameter_values.json
PARAMETERS=($(aws --profile ivl ssm describe-parameters --parameter-filters Key=Name,Option=BeginsWith,Values=OneView/dev/ | grep Name | sed 's/"Name": "//' | sed 's/",$//'))
# PARAMETERS=($(aws ssm describe-parameters --parameter-filters Key=Name,Option=BeginsWith,Values=OneView/dev/ | grep Name | sed 's/"Name": "//' | sed 's/",$//'))
PARAMETERS_ARGUMENT=

rm -f $OUTPUT_FILE

# echo '{'
# echo '    "Parameters": ['

for index in "${!PARAMETERS[@]}"; do
    # echo ${PARAMETERS[index]}
    # record=$(aws --profile ivl --no-paginate ssm get-parameters --with-decryption --names ${PARAMETERS[index]})
    # echo '        {'
    # echo $record | grep Name
    # echo $record | grep Value
    # echo '        },'
    if [[ $((($index+1) % 10)) = 0 ]]; then
        if [[ $index > 0 ]]; then
            # aws --profile ivl --no-paginate ssm get-parameters --with-decryption --names ${PARAMETERS_ARGUMENT} >> ${OUTPUT_FILE}
            aws --no-paginate ssm get-parameters --with-decryption --names ${PARAMETERS_ARGUMENT} >> ${OUTPUT_FILE}
        fi
        PARAMETERS_ARGUMENT="${PARAMETERS[index]}"
    else
        PARAMETERS_ARGUMENT+=" ${PARAMETERS[index]}"
    fi
done

# echo "    ]"
# echo "}"

# aws --profile ivl --no-paginate ssm get-parameters --with-decryption --names ${PARAMETERS_ARGUMENT} >> ${OUTPUT_FILE}
aws --no-paginate ssm get-parameters --with-decryption --names ${PARAMETERS_ARGUMENT} >> ${OUTPUT_FILE}
