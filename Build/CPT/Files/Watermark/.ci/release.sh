#!/usr/bin/env bash

set -u

ENVIRONMENT=${1:-""}


main() {
    declare -A VERSIONS=(
        [sbx]=dev
        [dev]=dev
        [tst]=1.0.1
        [itg]=1.0.1
        [prd]=1.0.1
    )

    if [[ "$ENVIRONMENT" != "" ]]; then
        export RELEASE_VERSION="${VERSIONS[$ENVIRONMENT]}"
    fi

    export RELEASE_TYPE="Python"
    export RELEASE_NAME="datalabs-cpt-files-watermark"
    export RELEASE_DESCRIPTION="CPT Release Distribution Watermarking DAG"
}


main
