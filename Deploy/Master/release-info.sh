#!/usr/bin/env bash

set -eux


main() {
    tag=$1
    package=$(extract_package_name $tag)
    version=$(extract_package_version $tag)
    project=$(find_project $package)

    source Build/$project/.ci/release.sh sbx
    export RELEASE_VERSION=$version
    export PROJECT=$project
}


extract_package_name() {
    tag=$1
    package=${tag//_*/}

    echo $package | tr -d '\n'
}


extract_package_version() {
    tag=$1
    version=${tag/*_/}

    echo $version | tr -d '\n'
}

find_project() {
    package=$1
    declare -a projects=($(cat ./.ci/projects.txt))
    target_project=

    for project in ${projects[@]}; do
        release_script=Build/$project/.ci/release.sh

        if [[ -f "$release_script" ]]; then
            source $release_script sbx
        fi

        if [[ "$RELEASE_NAME" == "$package" ]]; then
            target_project=$project
            break
        fi
    done

    echo $target_project | tr -d '\n'
}


main "$@"
