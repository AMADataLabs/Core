#!/usr/bin/env bash

# Documentation
read -r -d '' USAGE_TEXT << EOM
Usage:
    list-projects-to-builds.sh <revision range>
    List all projects which had some changes in given commit range.
    Project is identified with relative path to project's root directory from repository root.
    Output list is ordered respecting dependencies between projects (lower projects depends on upper).
    There can be multiple projects (separated by space) on single line which means they can be build on parallel.

    If one of commit messages in given commit range contains [rebuild-all] flag then all projects will be listed.
    <revision reange>       range of revision hashes where changes will be looked for
                            format is HASH1..HASH2
EOM

set -ex

# Capture input parameter and validate it
COMMIT_RANGE=$1
COMMIT_RANGE_FOR_LOG="$(echo $COMMIT_RANGE | sed -e 's/\.\./.../g')"

if [[ -z $COMMIT_RANGE ]]; then
    echo "ERROR: You need to provide revision range in format HASH1..HASH2 as input parameter"
    echo "$USAGE_TEXT"
    exit 1
fi

# Find script directory (no support for symlinks)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

export VIRTUAL_ENV="${DIR}/../Environment/Master"
export PATH="$VIRTUAL_ENV/bin:$PATH"

# Look for changes in given revision range
CHANGED_PATHS=$(git diff --name-status $COMMIT_RANGE --)
#echo -e "Changed paths:\n$CHANGED_PATHS"

# Look for dependencies between projects
PROJECT_DEPENDENCIES=$(${DIR}/list-dependencies.sh)

# Setup variables for output collecting
CHANGED_PROJECTS=""
CHANGED_DEPENDENCIES=""

##
# Recursively look for projects which depend on the given project.
# Outputs lines of tuples in format PROJECT1 PROJECT2 (separated by space),
# where PROJECT1 depends on PROJECT2.
#
# Input:
#   PROJECT - id of project
##
function process_dependants {
    local PROJECT=$1
    local DEPENDENCIES=$(echo "$PROJECT_DEPENDENCIES" | grep ".* $PROJECT_DIR")
    echo "$NEW_DEPENDENCEIS" | while read DEPENDENCY; do
        DEPENDENCY=$(echo "$DEPENDENCY" | cut -d " " -f1)
        if [[ ! $(echo "$CHANGED_PROJECTS" | grep "$DEPENDENCY") ]]; then
            CHANGED_SOURCES=
            for SOURCE_FILE in $(${DIR}/run.py python3.7 ${DIR}/list_source_dependencies.py $PROJECT); do
                if [[ $(echo -e "$CHANGED_PATHS" | grep "$SOURCE_FILE") ]]; then
                    CHANGED_SOURCES="$CHANGED_SOURCES\n$SOURCE_FILE"
                fi
            done

            if [[ -z $CHANGED_SOURCES ]]; then
                NEW_DEPENDENCEIS="$DEPENDENCIES\n$(process_dependants $DEPENDENCY)"
            fi
        fi
    done
    echo -e "$DEPENDENCIES"
}

# If [rebuild-all] command passed it's enough to take all projects and all dependencies as changed
if [[ $(git log "$COMMIT_RANGE_FOR_LOG" | grep "\[rebuild-all\]") ]]; then
    CHANGED_PROJECTS=$(cat ${DIR}/../.ci/projects.txt)
    CHANGED_DEPENDENCIES="$PROJECT_DEPENDENCIES"
else
    # For all known projects check if there was a change and look for all dependant projects
    # echo "Changed Paths:\n$CHANGED_PATHS"
    for PROJECT_DIR in $(cat ${DIR}/../.ci/projects.txt); do
        PROJECT_NAME=$(cat ${DIR}/../Build/${PROJECT_DIR}/.ci/project.txt)
        if [[ $(echo -e "$CHANGED_PATHS" | grep "$PROJECT_DIR") ]]; then
            CHANGED_PROJECTS="$CHANGED_PROJECTS\n$PROJECT_NAME"
            CHANGED_DEPENDENCIES="$CHANGED_DEPENDENCIES\n$(process_dependants $PROJECT_DIR)"
        else
            for SOURCE_FILE in $(${DIR}/run.py python3.7 ${DIR}/list_source_dependencies.py $PROJECT); do
                if [[ $(echo -e "$CHANGED_PATHS" | grep -e "$SOURCE_FILE" -e "Build/$PROJECT_DIR")  ]]; then
                    CHANGED_PROJECTS="$CHANGED_PROJECTS\n$PROJECT_NAME"
                    CHANGED_DEPENDENCIES="$CHANGED_DEPENDENCIES\n$(process_dependants $PROJECT_DIR)"
                fi
            done
        fi
    done
fi

# Build output
PROJECTS_TO_BUILD=$(echo -e "$CHANGED_DEPENDENCIES" | tsort | tac)
for PROJECT_NAME in $(echo -e "$CHANGED_PROJECTS"); do
    if [[ ! $(echo -e "$PROJECTS_TO_BUILD" | grep "$PROJECT_NAME") ]]; then
        PROJECTS_TO_BUILD="$PROJECT_NAME $PROJECTS_TO_BUILD"
    fi
done

# Print output
echo -e "$PROJECTS_TO_BUILD"
