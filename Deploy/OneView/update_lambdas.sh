#!/bin/bash

ENVIRONMENT=${1:-dev}

PROJECT=OneView
FUNCTIONS=(
    "addDepartment"
    "addOrg"
    "addProfile"
    "ageGenderMpaAnnual"
    "ageGenderMpa"
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
    "lambdaAuthorizer"
    "processAccessRequest"
    "removeDremioToken"
    "specialtyByMpaAnnual"
    "specialtyByMpa"
    "updateDepartment"
    "updateGroupUsers"
    "updateProfile"
    "updateUserDetails"
    "updateUserProfile"
    "validateUser"
)
LAYER_ARN=arn:aws:lambda:us-east-1:191296302136:layer:OneView-dev-webapp-lambda-layer:3
RUNTIME=python3.8

for name in ${FUNCTIONS[@]}; do
    function_name=${PROJECT}-${ENVIRONMENT}-${name}
    aws lambda update-function-configuration --function-name ${function_name} --runtime ${RUNTIME} --layers ${LAYER_ARN}
done
