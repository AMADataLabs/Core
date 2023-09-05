#!/usr/bin/env bash

set -u

ENVIRONMENT=${1:-""}


main() {
    declare -A VERSIONS=(
        [sbx]=dev
        [dev]=dev
        [tst]=2.0.3
        [prd]=2.0.3
    )

    if [[ "$ENVIRONMENT" != "" ]]; then
        export RELEASE_VERSION="${VERSIONS[$ENVIRONMENT]}"
    fi

    export RELEASE_TYPE="Java"
    export RELEASE_NAME="datalabs-amc-extract"
    export RELEASE_DESCRIPTION="AMC Address Flagging Report Extraction DAG plugin"
}


main
