#!/usr/bin/env bash

ENVIRONMENT=$1


main() {
    declare -A VERSIONS=(
        [sbx]=dev
        [dev]=dev
        [tst]=1.0.0
        [itg]=
        [prd]=1.0.0
    )

    if [[ "$ENVIRONMENT" != "" ]]; then
        export RELEASE_VERSION="${VERSIONS[$ENVIRONMENT]}"
    fi

    export RELEASE_TYPE="Python"
    export RELEASE_NAME="datalabs-amc"
    export RELEASE_DESCRIPTION="AMC Address Flagging Report DAG"
}


main
