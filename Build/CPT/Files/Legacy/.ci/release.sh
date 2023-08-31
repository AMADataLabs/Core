#!/usr/bin/env bash

set -u

ENVIRONMENT=${1:-""}


main() {
    declare -A VERSIONS=(
        [sbx]=dev
        [dev]=dev
        [tst]=0.2.0
        [prd]=0.2.0
    )

    if [[ "$ENVIRONMENT" != "" ]]; then
        export RELEASE_VERSION="${VERSIONS[$ENVIRONMENT]}"
    fi

    export RELEASE_TYPE="Java"
    export RELEASE_NAME="datalabs-cpt-files-legacy"
    export RELEASE_DESCRIPTION="CPT Files Builder legacy Java app wrapper tasks"
}


main
