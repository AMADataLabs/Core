#!/usr/bin/env bash

ENVIRONMENT=$1


main() {
    declare -A VERSIONS=(
        [sbx]=dev
        [dev]=dev
        [tst]=1.0.0
        [itg]=1.0.0
        [prd]=1.0.0
    )

    export RELEASE_NAME="datalabs-scheduler"
    export RELEASE_VERSION="${VERSIONS[$ENVIRONMENT]}"
    export RELEASE_DESCRIPTION="cloud-native DAG execution components"
}



if [[ "$ENVIRONMENT" == "" ]]; then
    echo "Error: missing environment argument"
else
    main
fi
