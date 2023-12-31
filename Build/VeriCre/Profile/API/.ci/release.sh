#!/usr/bin/env bash

set -u

ENVIRONMENT=${1:-""}


main() {
    declare -A VERSIONS=(
        [sbx]=dev
        [dev]=dev
        [tst]=1.1.4
        [itg]=1.1.4
        [prd]=1.1.4
    )

    if [[ "$ENVIRONMENT" != "" ]]; then
        export RELEASE_VERSION="${VERSIONS[$ENVIRONMENT]}"
    fi

    export RELEASE_TYPE="Python"
    export RELEASE_NAME="datalabs-vericre-profile-api"
    export RELEASE_DESCRIPTION="VeriCre Profiles API implementations"
}


main
