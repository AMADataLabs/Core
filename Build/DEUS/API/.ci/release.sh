#!/usr/bin/env bash
set -u
ENVIRONMENT=${1:-""}
main() {
    declare -A VERSIONS=(
        [sbx]=dev
        [dev]=dev
        [tst]=1.0.0
        [itg]=1.0.0
        [prd]=1.0.0
    )
    if [[ "$ENVIRONMENT" != "" ]]; then
        export RELEASE_VERSION="${VERSIONS[$ENVIRONMENT]}"
    fi
    export RELEASE_TYPE="Python"
    export RELEASE_NAME="datalabs-deus-api"
    export RELEASE_DESCRIPTION="DEUS backend API"
}
main

