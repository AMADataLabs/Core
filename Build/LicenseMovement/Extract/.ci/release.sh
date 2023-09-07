#!/usr/bin/env bash

set -u

ENVIRONMENT=${1:-""}


main() {
    declare -A VERSIONS=(
        [sbx]=dev
        [dev]=dev
        [tst]=dev
        [prd]=2.0.0
    )

    if [[ "$ENVIRONMENT" != "" ]]; then
        export RELEASE_VERSION="${VERSIONS[$ENVIRONMENT]}"
    fi

    export RELEASE_TYPE="Java"
    export RELEASE_NAME="datalabs-license-movement-extract"
    export RELEASE_DESCRIPTION="License Movement EXTRACT"
}


main
