determine_package_info() {
    source Build/${PROJECT}/.ci/release.sh $ENVIRONMENT

    if [[ "$RELEASE_TYPE" == "Python" ]]; then
        determine_python_package_info
    elif [[ "$RELEASE_TYPE" == "Java" ]]; then
        determine_java_package_info
    else
        echo "Error: invalid runtime "'"'"$RELEASE_TYPE"'"'""
        exit 1
    fi
}


determine_python_package_info() {
    local version=$RELEASE_VERSION
    local return_code=0

    if [[ "$version" == "dev" ]]; then
        version=$(
            aws --profile default codeartifact list-package-versions \
                --domain datalabs --repository datalabs-sbx --package $RELEASE_NAME \
                --format pypi --sort-by PUBLISHED_TIME | jq -r '.versions[0].version'
        )

        if [[ ${PIPESTATUS[0]} != 0 ]]; then
            echo "Error: Package ${RELEASE_NAME} does not exist."
            return_code=${PIPESTATUS[0]}
        fi
    fi

    PACKAGE="$RELEASE_NAME"
    VERSION="$version"
    METADATA='--metadata {"package_version":"'${version}'"}'

    return $return_code
}


determine_java_package_info() {
    local package=${RELEASE_NAME#datalabs-}
    local version=$RELEASE_VERSION
    local return_code=0

    if [[ "$version" == "dev" ]]; then
        version=$(
            aws --profile default codeartifact list-package-versions \
                --domain datalabs --repository datalabs-sbx --namespace org.ama-assn.datalabs --package $package \
                --format maven --sort-by PUBLISHED_TIME | jq -r '.versions[0].version'
        )

        if [[ ${PIPESTATUS[0]} != 0 ]]; then
            echo "Error: Package ${package} does not exist."
            return_code=${PIPESTATUS[0]}
        fi
    fi

    PACKAGE="$package"
    VERSION="$version"
    METADATA='--metadata {"package_version":"'${version}'"}'

    return $return_code
}
