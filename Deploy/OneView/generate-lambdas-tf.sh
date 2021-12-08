#!/bin/bash

declare -a RAW_NAMES
declare -a TIMEOUTS

LAMBDA_DATA=(
    "addDepartment:3"
    "addFilter:20"
    "addOrg:3"
    "addProfile:3"
    "addSavedColumn:3"
    "addUsers:20"
    "ageGenderMpaAnnual:20"
    "ageGenderMpa:20"
    "dpcByAgeAnnual:180"
    "getAdminUsers:3"
    "getAffiliationMasterData:20"
    "getBusinessMasterData:20"
    "getCounties:20"
    "getDatalabsQuestions:20"
    "getDepartment:3"
    "getDepartments:3"
    "getDremioToken:3"
    "getFilters:20"
    "getGroupUsers:20"
    "getMTPMasterData:20"
    "getOneviewData:900"
    "getOneviewQuestions:20"
    "getOrgMasterData:20"
    "getOrgs:3"
    "getPhysicianAffiliations:20"
    "getPhysicianColumns:20"
    "getPhysicianContactMasterData:20"
    "getPowerBIReportEmbedConfig:20"
    "getProfile:3"
    "getProfiles:3"
    "getResources:3"
    "getSavedColumns:3"
    "getToken:10"
    "getUserDetails:3"
    "getUsers:3"
    "lambdaAuthorizer:3"
    "physicianTypeEthnicity:20"
    "physicianTypeEthnicityAnnual:20"
    "processAccessRequest:30"
    "removeDremioToken:3"
    "saveDatalabsFeedback:20"
    "saveOneviewFeedback:20"
    "specialtyByMpaAnnual:20"
    "specialtyByMpa:20"
    "updateDepartment:3"
    "updateGroupUsers:20"
    "updateProfile:3"
    "updateUserDetails:3"
    "updateUserProfile:3"
    "userDataNowFiles:5"
    "validateUser:3"
    "workforceStatsAnnual:180"
)

SNAKE_CASE_NAMES=()


main() {
    breakout_lambda_data

    initialize_lambdas_tf

    initialize_update_lambdas_sh

    generate_snake_case_names

    generate_code
}


breakout_lambda_data() {
    for datum in "${LAMBDA_DATA[@]}" ; do
        name=${datum%%:*}
        timeout=${datum#*:}
        RAW_NAMES+=($name)
        TIMEOUTS+=($timeout)
    done
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

PROJECT="\${PROJECT:-OneView}"
ENVIRONMENT="\${ENVIRONMENT:-sbx}"

\$(apigw_assume_role.sh \$ENVIRONMENT | grep source)


CODE_BUCKET="ama-\${ENVIRONMENT}-datalake-lambda-us-east-1"
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


echo "### Generating lambdas.tf ###"
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

    echo "### Generating update_lambdas.sh ###"
    cat functions.txt >> update_lambdas.sh

    cat >> update_lambdas.sh << EOF
)
BUNDLES=(
EOF

    cat bundles.txt >> update_lambdas.sh

    cat >> update_lambdas.sh << EOF
)

for index in "\${!FUNCTIONS[@]}"; do
  aws --no-paginate lambda update-function-code --function-name \${FUNCTIONS[index]} --s3-bucket \${CODE_BUCKET} --s3-key \${BUNDLES[index]} || exit \$?
done
EOF
}

rm lambda.tf
rm functions.txt
rm bundles.txt

main
