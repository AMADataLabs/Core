#!/bin/bash

# Set up variables
CWD=$(realpath .)
VIRTUAL_ENV=${CWD}/Environment/Master
RUN="python3 ${CWD}/Script/run.py"
TEMPLATE_FILES="${CWD}/Build/Master/requirements_template.txt ${CWD}/Build/Master/Pipfile_template.txt ${CWD}/Build/Master/conda_requirements_template.txt"


main() {
    setup_test_files

    run_tests
}


setup_test_files() {
    cp ${TEMPLATE_FILES} ${CWD}/Test/Python/test/datalabs/environment/
}


run_tests() {
    setup_virtualenv

    ${RUN} ${VIRTUAL_ENV}/bin/pytest \
        -vv Test/Python/ Test/Python/test/datalabs/build/ \
        -W ignore::DeprecationWarning
}


setup_virtualenv() {
    export PATH="${VIRTUAL_ENV}/bin:${PATH}"
}

main
