#!/bin/bash

SNAKE_CASE_NAMES='add_department add_profile get_admin_users get_data_now_token get_department get_departments get_group_users get_orgs get_profile get_profiles get_resources get_token get_user_details get_users lambdaAuthorizer process_access_request remove_data_now_token update_department update_group_users update_profile update_user_details update_user_profile validate_user'

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

  render-template -t lambda.tf.jinja -f $CAMEL_CASE_NAME.tf -v "SNAKE_CASE_NAME=${name},DASHED_NAME=${DASHED_NAME},HUMAN_READABLE_NAME=${HUMAN_READABLE_NAME},CAMEL_CASE_NAME=${CAMEL_CASE_NAME}"
done
