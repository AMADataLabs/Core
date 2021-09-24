#!/bin/bash

RAW_NAMES=(
    "addDepartment"
    "addOrg"
    "addProfile"
    "age-gender-mpa-annual"
    "age-gender-mpa"
    "getAdminUsers"
    "getCounties"
    "getDepartment"
    "getDepartments"
    "getDremioToken"
    "getGridMasterData"
    "getGroupUsers"
    "getOneviewData"
    "getOrgs"
    "getPhysicianColumns"
    "getProfile"
    "getProfiles"
    "getResources"
    "getToken"
    "getUserDetails"
    "getUsers"
    "processAccessRequest"
    "removeDremioToken"
    "specialty-by-mpa-annual"
    "specialty-by-mpa"
    "updateDepartment"
    "updateGroupUsers"
    "updateProfile"
    "updateUserDetails"
    "updateUserProfile"
    "validateUser"
)
SNAKE_CASE_NAMES=

for name in ${RAW_NAMES[@]}; do
    name=${name//-/_}
    name=$(echo $name | sed 's/\([A-Z]\)/_\1/g' | tr '[:upper:]' '[:lower:]')
    SNAKE_CASE_NAMES+="$name "
done

rm -f lambdas.tf
rm -f functions.txt
rm -f bundles.txt

for name in $SNAKE_CASE_NAMES; do
  DASHED_NAME=${name//_/-}
  HUMAN_READABLE_NAME=""
  CAMEL_CASE_NAME=""
  parts=${name//_/ }

  for part in $parts; do
    capitalized_part="$(tr '[:lower:]' '[:upper:]' <<< ${part:0:1})${part:1}"
    HUMAN_READABLE_NAME="${HUMAN_READABLE_NAME} $capitalized_part"
    CAMEL_CASE_NAME="${CAMEL_CASE_NAME}$capitalized_part"
  done

  CAMEL_CASE_NAME="$(tr '[:upper:]' '[:lower:]' <<< ${CAMEL_CASE_NAME:0:1})${CAMEL_CASE_NAME:1}"

  render-template -t lambda.tf.jinja -f lambda.tf -v "SNAKE_CASE_NAME=${name},DASHED_NAME=${DASHED_NAME},HUMAN_READABLE_NAME=${HUMAN_READABLE_NAME},CAMEL_CASE_NAME=${CAMEL_CASE_NAME}"

  cat lambda.tf >> lambdas.tf

  echo "    "'"'"\${PROJECT}-\${ENVIRONMENT}-${CAMEL_CASE_NAME}"'"'"" >> functions.txt
  echo "    "'"'"\${PROJECT}/${CAMEL_CASE_NAME}.zip"'"'"" >> bundles.txt
done

rm lambda.tf
