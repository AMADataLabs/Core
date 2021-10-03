#!/bin/bash

PARAMETERS=(
    "/OneView/dev/api_gateway_url"
    "/OneView/dev/app_url"
    "/OneView/dev/data_now_url"
    "/OneView/dev/masterfile_dbhost"
    "/OneView/dev/masterfile_dbname"
    "/OneView/dev/masterfile_dbpassword"
    "/OneView/dev/masterfile_dbport"
    "/OneView/dev/masterfile_user_name"
    "/OneView/dev/s3_url"
    "/OneView/dev/sso_authroziation_url"
    "/OneView/dev/sso_client_id"
    "/OneView/dev/sso_client_secret"
    "/OneView/dev/sso_logout_url"
    "/OneView/dev/sso_redirect_uri"
    "/OneView/dev/token_url"
    "/OneView/dev/usrmgmt_dbhost"
    "/OneView/dev/usrmgmt_dbname"
    "/OneView/dev/usrmgmt_dremio_password"
    "/OneView/dev/usrmgmt_dremio_remove_token_url"
    "/OneView/dev/usrmgmt_dremio_url"
    "/OneView/dev/usrmgmt_dremio_user_id"
    "/OneView/dev/usrmgmt_fromEmail"
    "/OneView/dev/usrmgmt_password"
    "/OneView/dev/usrmgmt_smtpPassword"
    "/OneView/dev/usrmgmt_smtpURL   "
    "/OneView/dev/usrmgmt_user_name"
 )
 PARAMETERS_ARGUMENT=

for index in "${!PARAMETERS[@]}"; do
  if [[ $((($index+1) % 10)) = 0 ]]; then
      if [[ $index > 0 ]]; then
          aws --profile ivl --no-paginate ssm get-parameters --with-decryption --names ${PARAMETERS_ARGUMENT}
      fi
      PARAMETERS_ARGUMENT="${PARAMETERS[index]}"
  else
      PARAMETERS_ARGUMENT+=" ${PARAMETERS[index]}"
  fi
done
