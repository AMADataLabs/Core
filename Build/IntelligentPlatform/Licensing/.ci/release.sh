#!/usr/bin/env bash

set -u

ENVIRONMENT=${1:-""}


main() {
    declare -A VERSIONS=(
        [sbx]=[dev]=dev
        [tst]=2.0.0
        [prd]=2.0.0
    )

    if [[ "$ENVIRONMENT" != "" ]]; then
        export RELEASE_VERSION="${VERSIONS[$ENVIRONMENT]}"
    fi

    export RELEASE_TYPE="Python"
    export RELEASE_NAME="datalabs-intelligentplatform-licensing"
    export RELEASE_DESCRIPTION="Intelligent Platform Licensing ETL Process"
}


main
