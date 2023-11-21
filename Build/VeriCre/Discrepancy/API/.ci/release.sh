#!/usr/bin/env bash

set -u

ENVIRONMENT=${1:-""}


main() {
    declare -A VERSIONS=(
        [sbx]=dev
        [dev]=dev
        [tst]=0.1.0.dev0
        [itg]=0.1.0.dev0
        [prd]=0.1.0.dev0
    )

    if [[ "$ENVIRONMENT" != "" ]]; then
        export RELEASE_VERSION="${VERSIONS[$ENVIRONMENT]}"
    fi

    export RELEASE_TYPE="Python"
    export RELEASE_NAME="datalabs-vericre-discrepancy-api"
    export RELEASE_DESCRIPTION="VeriCre Discrepancy API endpoint implementations"
}


main
