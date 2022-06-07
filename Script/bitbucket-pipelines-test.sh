#!/usr/bin/env bash

set -ex

Script/setup-virtual-environment Master
export VIRTUAL_ENV=${PWD}/Environment/Master
export PATH="$VIRTUAL_ENV/bin:$PATH"

# Find script directory (no support for symlinks)
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

# Configuration with default values
: "${CI_TOOL:=bitbucket}"
: "${CI_PLUGIN:=$DIR/plugins/${CI_TOOL}.sh}"

# Resolve commit range for current build
LAST_SUCCESSFUL_COMMIT=$(${CI_PLUGIN} hash last)
echo "Last commit: ${LAST_SUCCESSFUL_COMMIT}"
if [[ ${LAST_SUCCESSFUL_COMMIT} == "null" ]]; then
    COMMIT_RANGE="origin/master"
else
    COMMIT_RANGE="$(${CI_PLUGIN} hash current)..${LAST_SUCCESSFUL_COMMIT}"
fi
echo "Commit range: $COMMIT_RANGE"

# Ensure we have all changes from last successful build
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

python Script/run.py python -m pytest Test/Python/ Test/Python/test/datalabs/build/ -W ignore::DeprecationWarning

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
        PROJECT=$(cat ${DIR}/../Build/${PROJECT_DIR}/.ci/project.txt)

        if [[ "$PROJECT" == "$TARGET_PROJECT" ]]; then
            TARGET_DIR=$PROJECT_DIR
            break
        fi
    done

    if [[ "$TARGET_DIR" != "" ]]; then
        FILES="$FILES $(${DIR}/run.py python3.7 ${DIR}/list_source_dependencies.py $TARGET_DIR)"
    fi
done

# Dedup files list
FILES_TO_LINT=
for FILE in $FILES; do
    echo $FILES_TO_LINT | grep -w -q $FILE
    if [[ $? = 1 ]]; then
        FILES_TO_LINT="$FILES_TO_LINT $FILE"
    fi
done

FILES_TO_LINT="$(find ${PWD}/Source/Python/datalabs -name "*.py"  | grep -v ${PWD}/Source/Python/datalabs/airflow | tr '\n' ' ') $(find ${PWD}/Test/Python/test/datalabs -name "*.py" | tr '\n' ' ')"

${DIR}/run.py pylint --extension-pkg-whitelist=pyodbc,numpy $FILES_TO_LINT
