#!/usr/bin/env bash

##
# Main entry for monorepository build.
# Triggers builds for all modified projects in order respecting their dependencies.
#
# Usage:
#   bitbucket-pipelines-build
#
# Adapted from https://github.com/zladovan/monorepo/blob/master/tools/ci/core/build.sh
##

echo $(python3 --version)

Script/setup-virtual-environment Master/BitBucketPipelines
export VIRTUAL_ENV=${PWD}/Environment/Master/BitBucketPipelines
export PATH="$VIRTUAL_ENV/bin:$PATH"

# Find script directory (no support for symlinks)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

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

# Run tests
echo "Running tests..."
CI_PLUGIN=${CI_PLUGIN} $DIR/build-projects.sh Test

if [[ $? != 0 ]]; then
    echo "Tests failed. Aborting build..."
    exit 1
fi

# Collect all modified projects
PROJECTS_TO_BUILD=$($DIR/list-projects-to-build.sh $COMMIT_RANGE)

# If nothing to build inform and exit
if [[ -z "$PROJECTS_TO_BUILD" ]]; then
    echo "No projects to build"
    exit 0
fi

echo "Following projects need to be built"
echo -e "$PROJECTS_TO_BUILD"

# Build all modified projects
echo -e "$PROJECTS_TO_BUILD" | while read PROJECTS; do
    CI_PLUGIN=${CI_PLUGIN} $DIR/build-projects.sh ${PROJECTS_TO_BUILD}
done;
