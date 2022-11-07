#!/usr/bin/env bash

set -u

ENVIRONMENT=${1:-""}


main() {
    declare -A VERSIONS=(
        [sbx]=dev
        [dev]=dev
        [tst]=1.1.1
        [itg]=1.1.1
        [prd]=1.1.1
    )

    if [[ "$ENVIRONMENT" != "" ]]; then
        export RELEASE_VERSION="${VERSIONS[$ENVIRONMENT]}"
    fi

    export RELEASE_TYPE="Python"
    export RELEASE_NAME="datalabs-cerner-report"
    export RELEASE_DESCRIPTION="Cerner report DAG"
}


main
