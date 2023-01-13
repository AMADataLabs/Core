#!/bin/bash

SCRIPT_PATH=`realpath $0`
SCRIPT_BASE_PATH=`dirname $SCRIPT_PATH`

MODULE=$1
VARIABLES=


main() {
    extract_variables

    generate_main

    generate_variables

    generate_outputs

    copy_locals
}


extract_variables() {
    VARIABLES=(`cat ${MODULE}/variables.tf | grep 'variable "' | sed -e 's/variable "//' -e 's/" {//'`)
}


generate_main() {
    echo 'module "this" {' > main.tf
    echo "  source = \"./${MODULE}\"" >> main.tf

    for variable in "${VARIABLES[@]}" ; do
        if [[ "$variable" != "tags" ]]; then
            echo "  ${variable} = var.${variable}" >> main.tf
        fi
    done

    echo "  tags = local.tags" >> main.tf

    echo '}' >> main.tf

    terraform fmt main.tf
}


generate_variables() {
    cat ${MODULE}/variables.tf ${SCRIPT_BASE_PATH}/tags.txt > variables.tf

    terraform fmt variables.tf
}


generate_outputs() {
    awk -f ${SCRIPT_BASE_PATH}/generate_outputs.awk ${MODULE}/outputs.tf > outputs.tf

    terraform fmt outputs.tf
}

copy_locals() {
    cp ${SCRIPT_BASE_PATH}/locals.tf ./
}


main "$@"
