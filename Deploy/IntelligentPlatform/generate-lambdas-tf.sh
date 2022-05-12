#!/usr/bin/env bash

declare -a RAW_NAMES
declare -a TIMEOUTS

LAMBDA_TEMPLATE=lambda.tf.jinja

LAMBDA_DATA=(
    "addDLUser:26"
    "addOrg:5"
    "addUsers:30"
    "bulkEditUsers:18"
    "checkOrganizationExists:5"
    "checkOrganizationExistsFL:5"
    "checkProductExists:5"
    "checkSubmittedQuote:5"
    "createAgreementDetail:28"
    "createAgreementDetailFL:28"
    "createNewQuote:20"
    "clearTokens:45"
    "contactBackDetail:28"
    "deleteTaxExemptCertificate:5"
    "getAgreementDetail:5"
    "getAgreementDetailFL:5"
    "getAPILicenseTypes:5"
    "getAPIRateLimits:5"
    "getCategories:5"
    "getContent:5"
    "getDLLicenseAgreementContent:5"
    "getDomains:5"
    "getExistingCustomers:5"
    "getOrg:5"
    "getOrgSuggestions:5"
    "getOrgs:18"
    "getPermissions:5"
    "getProductSuggestions:20"
    "getQuestions:45"
    "getQuotePrice:20"
    "getRefOrganizations:10"
    "getSources:5"
    "getToken:75"
    "getTabContent:20"
    "getTaxExemptS3BucketSignedURL:20"
    "getTypes:5"
    "getUserDetails:60"
    "getUsers:25"
    "lambdaAuthorizer:3"
    "listGroups:18"
    "listRoles:18"
    "saveContent:5"
    "saveEmailSuggestions:20"
    "saveFeedback:45"
    "saveTabContent:20"
    "submitQuote:28"
    "submitQuoteFL:28"
    "updateOrg:18"
    "updateTaxExemptCertificates:5"
    "updateUserDetails:30"
    "updateUserPermissions:26"
    "validateUser:18"
)

SNAKE_CASE_NAMES=()


main() {
    cleanup_old_files

    breakout_lambda_data

    initialize_lambdas_tf

    initialize_update_lambdas_sh

    generate_snake_case_names

    generate_code
}

cleanup_old_files() {
    rm -f lambda.tf
    rm -f functions.txt
    rm -f bundles.txt
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

data "aws_s3_bucket_object" "authpython_layer_hash" {
  bucket = local.s3_lambda_bucket
  key    = "authpython.zip"
}

resource "aws_lambda_layer_version" "authpython" {
    layer_name              = "AIP-\${local.environment}-authpython-lambda-layer"
    description             = "Intelligent Platform web app backend Lambda function base layer"
    s3_bucket               = local.s3_lambda_bucket
    s3_key                  = "authpython.zip"
    s3_object_version       = data.aws_s3_bucket_object.authpython_layer_hash.version_id
    compatible_runtimes     = ["python3.8"]
}
EOF
}


initialize_update_lambdas_sh() {
    cat > update_lambdas.sh << EOF
#!/usr/bin/env bash

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

        render-template -t ${LAMBDA_TEMPLATE} -f lambda.tf -V "TIMEOUT=${timeout},SNAKE_CASE_NAME=${name},DASHED_NAME=${DASHED_NAME},HUMAN_READABLE_NAME=${HUMAN_READABLE_NAME},CAMEL_CASE_NAME=${CAMEL_CASE_NAME}"

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

main
