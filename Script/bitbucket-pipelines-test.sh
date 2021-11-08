#!/bin/bash

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

Script/setup-virtual-environment Master
export VIRTUAL_ENV=${PWD}/Environment/Master
export PATH="$VIRTUAL_ENV/bin:$PATH"

python Script/run.py python -m pytest Test/Python/ Test/Python/test/datalabs/build/ -W ignore::DeprecationWarning

# Collect all modified projects
PROJECTS_TO_LINT=$($DIR/list-projects-to-build.sh $COMMIT_RANGE)

# If nothing to lint inform and exit
if [[ -z "$PROJECTS_TO_LINT" ]]; then
    echo "No projects to lint"
    exit 0
fi

echo "Following projects need to be linted"
echo -e "$PROJECTS_TO_LINT"

# Get files for all modified projects
FILES=
for TARGET in $PROJECTS_TO_LINT; do
    PROJECT=${TARGET/-${BITBUCKET_BRANCH}/}
    FILES="$FILES $(${DIR}/run.py python3.7 ${DIR}/list_source_dependencies.py $PROJECT)"
done;

# Dedup files list
FILES_TO_LINT=
for FILE in $FILES; do
    echo $FILES_TO_LINT | grep -w -q $FILE
    if [[ $? = 1 ]]; then
        FILES_TO_LINT="$FILES_TO_LINT $FILE"
    fi
done

if [[ $BITBUCKET_BRANCH == 'master' || $BITBUCKET_BRANCH == 'dev' ]]; then
    ${DIR}/run.py pylint --extension-pkg-whitelist=pyodbc,numpy $FILES_TO_LINT
else
    ${DIR}/run.py pylint --extension-pkg-whitelist=pyodbc,numpy --ignore=airflow ${PWD}/Source/Python/datalabs/* ${PWD}/Test/Python/test/datalabs/*
fi
