#!/usr/bin/env bash

set -u

ENVIRONMENT=${1:-""}


main() {
    declare -A VERSIONS=(
        [sbx]=[dev]=dev
        [tst]=[prd]=0.1.0
    )

    if [[ "$ENVIRONMENT" != "" ]]; then
        export RELEASE_VERSION="${VERSIONS[$ENVIRONMENT]}"
    fi

    export RELEASE_TYPE="Python"
    export RELEASE_NAME="datalabs-vericre-data-steward"
    export RELEASE_DESCRIPTION="VeriCre Data Steward DAG"
}


main
