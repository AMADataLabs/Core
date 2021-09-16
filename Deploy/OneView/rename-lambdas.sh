#!/bin/bash

set -ex

ENVIRONMENT="${1:-sbx}"

BUNDLE_NAMES=(
    "age-gender-mpa-annual"
    "age-gender-mpa"
    "specialty-by-mpa-annual"
    "specialty-by-mpa"
)

for name in $BUNDLE_NAMES; do
  CAMEL_CASE_NAME=""
  parts=${name//-/ }

  for part in $parts; do
    capitalized_part="$(tr '[:lower:]' '[:upper:]' <<< ${part:0:1})${part:1}"
    CAMEL_CASE_NAME="${CAMEL_CASE_NAME}$capitalized_part"
  done

  CAMEL_CASE_NAME="$(tr '[:upper:]' '[:lower:]' <<< ${CAMEL_CASE_NAME:0:1})${CAMEL_CASE_NAME:1}"

  aws s3 mv s3://ama-${ENVIRONMENT}-datalake-lambda-us-east-1/OneView/${name}.zip \
            s3://ama-${ENVIRONMENT}-datalake-lambda-us-east-1/OneView/${CAMEL_CASE_NAME}.zip
done
