#!/usr/bin/env bash

set -x
INPUT_FILE=$1

if [[ "$INPUT_FILE" == "" ]]; then
    echo "Missing API spec file argument."
    exit 1
fi

SUBSTITUTIONS=(
    's/title: "mfoneview"/title: "OneView App"/'
    's/"'"'"'\*'"'"'"/"'"'"'https:\/\/datalabs${host_suffix}.${domain}'"'"'"/'
    's/:us-east-1:/:${region}:/g'
    's/:655665223663:/:${account}:/'
    's/:mfoneview-/:${project}-${environment}-/'
    's/\${stageVariables.alias}/\$\${stageVariables.alias}/'
    's/-lambdaAuthorizer\/invocations/-lambdaAuthorizer:\$\${stageVariables.alias}\/invocations/'
    's/-age-gender-mpa-annual/-ageGenderMpaAnnual/'
    's/-specialty-by-mpa/-specialtyByMpa/'
    's/-physician-type-ethnicity-annual/-physicianTypeEthnicityMpa/'
    's/-physician-type-ethnicity/-physicianTypeEthnicity/'
    's/-dpc-by-age-annual/-dpcByAgeAnnual/'
    's/-workforce-stats-annual/-workforceStatsAnnual/'
)

COMMAND="cat $INPUT_FILE"

for substitution in "${SUBSTITUTIONS[@]}" ; do
    COMMAND+=" | sed $substitution"
done


$COMMAND
