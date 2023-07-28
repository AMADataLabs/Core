# #!/usr/bin/env bash
# set -u
# ENVIRONMENT=${1:-""}
# main() {
#     declare -A VERSIONS=(
#         [sbx]=dev
#         [dev]=dev
#         [tst]=1.0.0
#         [itg]=1.0.0
#         [prd]=1.0.0
#     )
#     if [[ "$ENVIRONMENT" != "" ]]; then
#         export RELEASE_VERSION="${VERSIONS[$ENVIRONMENT]}"
#     fi
#     export RELEASE_TYPE="Python"
#     export RELEASE_NAME="datalabs-deus-api"
#     export RELEASE_DESCRIPTION="DEUS backend API"
# }
# main

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

    # Generate the development version
    generate_dev_version
}

generate_dev_version() {
    # Query the AWS CodeArtifact repository for package versions
    current_version=$(aws --profile default codeartifact list-package-versions --domain datalabs --repository datalabs-sbx --package datalabs-deus-api --format pypi --sort-by PUBLISHED_TIME 2>/dev/null | jq -r '.versions[0].version')

    if [[ -z "$current_version" ]]; then
        # The package doesn't exist in the repository, set a default development version
        current_version="0.1.0"
    fi

    # Extract base version (e.g., 0.1.0) and dev version (e.g., 0.1.0) from the current version
    base_version=$(echo "$current_version" | sed 's/\.dev.*//')
    dev_version=$(echo "$current_version" | sed 's/..*dev//')

    # Check if the base version is "0.1.0" (package doesn't exist) or set any other actions as needed.
    if [[ "$base_version" == "0.1.0" ]]; then
        # The package doesn't exist in the repository, take appropriate actions if needed.
        # For example, you can print an informative message or exit the script.
        echo "Package datalabs-deus-api not found in the repository datalabs-sbx."
        echo "Setting default development version."
    fi

    # Print the generated development version (for debugging purposes)
    echo "Development version: $dev_version"
}

main
