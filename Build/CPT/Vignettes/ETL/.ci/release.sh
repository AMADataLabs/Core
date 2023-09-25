#!/usr/bin/env bash

set -u

ENVIRONMENT=${1:-""}


main() {
    declare -A VERSIONS=(
        [sbx]=dev
        [dev]=dev
        [tst]=dev
        [prd]=1.0.0
    )

    if [[ "$ENVIRONMENT" != "" ]]; then
        export RELEASE_VERSION="${VERSIONS[$ENVIRONMENT]}"
    fi

    export RELEASE_TYPE="Python"
    export RELEASE_NAME="datalabs-vignettes-etl"
    export RELEASE_DESCRIPTION="Vignettes CPT API ETL DAG definition and tasks"
}


main
