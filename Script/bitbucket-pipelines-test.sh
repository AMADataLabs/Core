#!/usr/bin/env bash

set -xe

# Find script directory (no support for symlinks)
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

# Configuration with default values
: "${CI_TOOL:=bitbucket}"
: "${CI_PLUGIN:=$DIR/plugins/${CI_TOOL}.sh}"

main() {
    return_code=0

    setup_virtual_environment

    create_maven_repo_config

    determine_commit_range

    get_changes_from_last_build

    run_python_unit_tests
    return_code=$?

    if [[ $? == 0 ]]; then
        run_java_unit_tests
        return_code=$?
    fi

    if [[ $? == 0 ]]; then
        run_lint_tests
        return_code=$?
    fi

    return $return_code
}


setup_virtual_environment() {
    Script/setup-virtual-environment Master

    export VIRTUAL_ENV=${PWD}/Environment/Master
    export PATH="$VIRTUAL_ENV/bin:$PATH"
}


create_maven_repo_config() {
    if [ -e ~/.m2/settings.xml ]; then
        echo "The file ~/.m2/settings.xml already exists. Skipping its creation..."
    else
        export CODEARTIFACT_AUTH_TOKEN=$(
            aws --profile default codeartifact get-authorization-token --domain datalabs\
            --query authorizationToken --output text
        )

        mkdir -p ~/.m2

        cat > ~/.m2/settings.xml <<EOF
<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0 https://maven.apache.org/xsd/settings-1.0.0.xsd">
    <servers>
        <server>
            <id>datalabs-sbx</id>
            <username>aws</username>
            <password>\${env.CODEARTIFACT_AUTH_TOKEN}</password>
        </server>
    </servers>
</settings>
EOF
    fi
}


determine_commit_range() {
    LAST_SUCCESSFUL_COMMIT=$(${CI_PLUGIN} hash last)

    echo "Last commit: ${LAST_SUCCESSFUL_COMMIT}"
    if [[ ${LAST_SUCCESSFUL_COMMIT} == "null" ]]; then
        COMMIT_RANGE="origin/master"
    else
        COMMIT_RANGE="$(${CI_PLUGIN} hash current)..${LAST_SUCCESSFUL_COMMIT}"
    fi

    echo "Commit range: $COMMIT_RANGE"
}


get_changes_from_last_build() {
    if [[ -f $(git rev-parse --git-dir)/shallow ]]; then
        if [[ ${LAST_SUCCESSFUL_COMMIT} == "null" ]]; then
            git fetch --unshallow
            git config remote.origin.fetch "+refs/heads/*:refs/remotes/origin/*"
            git fetch origin
        else
            DEPTH=1
            until git show ${LAST_SUCCESSFUL_COMMIT} > /dev/null 2>&1
            do
                DEPTH=$((DEPTH+5))
                echo "Last commit not fetched yet. Fetching depth $DEPTH."
                git fetch --depth=$DEPTH
            done
        fi
    fi
}


run_python_unit_tests() {
    python Script/run.py python3 -m pytest Test/Python/ Test/Python/test/datalabs/build/ -W ignore::DeprecationWarning

    return $?
}


run_java_unit_tests() {
    mvn test

    return $?
}


run_lint_tests() {
    # Collect all modified projects
    PROJECTS_TO_LINT=$($DIR/list-projects-to-build.sh $COMMIT_RANGE)

    # If nothing to lint inform and exit
    if [[ $BITBUCKET_BRANCH == 'master' && -z "$PROJECTS_TO_LINT" ]]; then
        echo "No projects to lint"
        exit 0
    fi

    echo "The following projects need to be linted"
    echo -e "$PROJECTS_TO_LINT"

    # Get files for all modified projects
    FILES=
    for TARGET_PROJECT in $PROJECTS_TO_LINT; do
        TARGET_DIR=

        for PROJECT_DIR in $(cat ${DIR}/../.ci/projects.txt); do
            if [[ "$PROJECT_DIR" == "$TARGET_PROJECT" ]]; then
                TARGET_DIR=$PROJECT_DIR
                break
            fi
        done

        if [[ "$TARGET_DIR" != "" ]]; then
            FILES="$FILES $(${DIR}/run.py python3 ${DIR}/list_source_dependencies.py $TARGET_DIR)"
        fi
    done

    # Dedup files list
    FILES_TO_LINT=
    for FILE in $FILES; do
        echo $FILES_TO_LINT | { grep -w -q $FILE || true; }
        if [[ $? = 1 ]]; then
            FILES_TO_LINT="$FILES_TO_LINT $FILE"
        fi
    done

    FILES_TO_LINT="$(find ${PWD}/Source/Python/datalabs -name "*.py"  | grep -v ${PWD}/Source/Python/datalabs/airflow | tr '\n' ' ') $(find ${PWD}/Test/Python/test/datalabs -name "*.py" | tr '\n' ' ')"

    ${DIR}/run.py pylint --extension-pkg-whitelist=pyodbc,numpy $FILES_TO_LINT

    return $?
}


main
