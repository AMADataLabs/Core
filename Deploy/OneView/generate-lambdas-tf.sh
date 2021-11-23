#!/bin/bash

RAW_NAMES=(
    "addDepartment"
    "addFilter"
    "addOrg"
    "addProfile"
    "addSavedColumn"
    "addUsers"
    "age-gender-mpa-annual"
    "age-gender-mpa"
    "dpc-by-age-annual"
    "getAdminUsers"
    "getAffiliationMasterData"
    "getBusinessMasterData"
    "getCounties"
    "getDatalabsQuestions"
    "getDepartment"
    "getDepartments"
    "getDremioToken"
    "getFilters"
    "getGroupUsers"
    "getMTPMasterData"
    "getOneviewData"
    "getOneviewQuestions"
    "getOrgMasterData"
    "getOrgs"
    "getPhysicianAffiliations"
    "getPhysicianColumns"
    "getPhysicianContactMasterData"
    "getProfile"
    "getProfiles"
    "getResources"
    "getSavedColumns"
    "getToken"
    "getUserDetails"
    "getUsers"
    "lambdaAuthorizer"
    "physician-type-ethnicity"
    "physician-type-ethnicity-annual"
    "processAccessRequest"
    "removeDremioToken"
    "saveDatalabsFeedback"
    "saveOneviewFeedback"
    "specialty-by-mpa-annual"
    "specialty-by-mpa"
    "updateDepartment"
    "updateGroupUsers"
    "updateProfile"
    "updateUserDetails"
    "updateUserProfile"
    "userDataNowFiles"
    "validateUser"
    "workforce-stats-annual"
)


TIMEOUTS=(
"3"
"20"
"3"
"3"
"3"
"20"
"20"
"20"
"180"
"3"
"20"
"20"
"20"
"20"
"3"
"3"
"3"
"20"
"20"
"20"
"900"
"20"
"20"
"3"
"20"
"20"
"20"
"3"
"3"
"3"
"3"
"10"
"3"
"3"
"3"
"20"
"20"
"30"
"3"
"20"
"20"
"20"
"20"
"3"
"20"
"3"
"3"
"3"
"5"
"3"
"180"
)

SNAKE_CASE_NAMES=()


main() {
    initialize_lambdas_tf

    initialize_update_lambdas_sh

    generate_snake_case_names

    generate_code
}


initialize_lambdas_tf() {
    cat > lambdas.tf << EOF
##### Lambdas - Web App #####

data "aws_s3_bucket_object" "layer_hash" {
  bucket = local.s3_lambda_bucket
  key    = "OneView/webapp-base-layer.zip"
}

resource "aws_lambda_layer_version" "webapp" {
    layer_name              = "\${var.project}-\${local.environment}-webapp-lambda-layer"
    description             = "OneView web app backend Lambda function base layer"
    s3_bucket               = local.s3_lambda_bucket
    s3_key                  = "OneView/webapp-base-layer.zip"
    s3_object_version       = data.aws_s3_bucket_object.layer_hash.version_id
    compatible_runtimes     = ["python3.8"]
}
EOF
}


initialize_update_lambdas_sh() {
    cat > update_lambdas.sh << EOF
#!/bin/bash

set -ex

PROJECT="${PROJECT:-OneView}"
ENVIRONMENT="${ENVIRONMENT:-sbx}"

CODE_BUCKET="ama-${ENVIRONMENT}-datalake-lambda-us-east-1"
FUNCTIONS=(
EOF
}


generate_snake_case_names() {
    for name in ${RAW_NAMES[@]}; do
        name=${name//-/_}
        name=$(echo $name | sed 's/\([A-Z]\)/_\1/g' | tr '[:upper:]' '[:lower:]')
        SNAKE_CASE_NAMES+=( $name )
    done
}


generate_code() {
    for index in ${!SNAKE_CASE_NAMES[@]}; do
        name=${SNAKE_CASE_NAMES[$index]}
        DASHED_NAME=${name//_/-}
        HUMAN_READABLE_NAME=""
        CAMEL_CASE_NAME=""
        parts=${name//_/ }
        timeout=${TIMEOUTS[$index]}

        for part in $parts; do
            capitalized_part="$(tr '[:lower:]' '[:upper:]' <<< ${part:0:1})${part:1}"
            HUMAN_READABLE_NAME="${HUMAN_READABLE_NAME} $capitalized_part"
            CAMEL_CASE_NAME="${CAMEL_CASE_NAME}$capitalized_part"
        done

        CAMEL_CASE_NAME="$(tr '[:upper:]' '[:lower:]' <<< ${CAMEL_CASE_NAME:0:1})${CAMEL_CASE_NAME:1}"

        render-template -t lambda.tf.jinja -f lambda.tf -v "TIMEOUT=${timeout},SNAKE_CASE_NAME=${name},DASHED_NAME=${DASHED_NAME},HUMAN_READABLE_NAME=${HUMAN_READABLE_NAME},CAMEL_CASE_NAME=${CAMEL_CASE_NAME}"

        cat lambda.tf >> lambdas.tf

        echo "    "'"'"\${PROJECT}-\${ENVIRONMENT}-${CAMEL_CASE_NAME}"'"'"" >> functions.txt
        echo "    "'"'"\${PROJECT}/${CAMEL_CASE_NAME}.zip"'"'"" >> bundles.txt
    done

    rm lambda.tf

    cat functions.txt >> update_lambdas.sh

    cat >> update_lambdas.sh << EOF
)
BUNDLES=(
EOF

    cat bundles.txt >> update_lambdas.sh

    cat >> update_lambdas.sh << EOF
)

for index in "${!FUNCTIONS[@]}"; do
  aws --no-paginate lambda update-function-code --function-name ${FUNCTIONS[index]} --s3-bucket ${CODE_BUCKET} --s3-key ${BUNDLES[index]} || exit $?
done
EOF
}


main
