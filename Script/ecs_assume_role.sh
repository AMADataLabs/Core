#!/usr/bin/env bash

environment=${1:-dev}
profile=${2:-shared}
filename=".ecs_token_${environment}_$(date +%Y%m%d%H%M%S)"
no_verify_ssl=

if [[ "$AWS_NO_VERIFY_SSL" == "True" ]]; then
  no_verify_ssl=--no-verify-ssl
fi

profile_available=0
for p in $(aws configure list-profiles); do
     if [[ "$p" == "$profile" ]]; then
         profile_available=1
     fi
done
if [[ $profile_available != 1 ]]; then
    echo "Missing AWS profile "'"'"$profile"'"'""
    exit 1
fi

declare account
case $environment in
    'dev')
        account=191296302136
    ;;
    'tst')
        account=194221139997
    ;;
    'stg')
        account=340826698851
    ;;
    'prd')
        account=285887636563
    ;;
esac

# access_key=$(aws configure get ${environment}.aws_access_key_id)
region=$(aws configure get ${profile}.region)

echo "Account: $account ($region)"

unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN


for i in $(aws sts ${no_verify_ssl} --profile ${profile} assume-role --role-arn "arn:aws:iam::${account}:role/ama-ecs-task-deployment" --role-session-name datalabs | egrep "AccessKeyId|SecretAccessKey|SessionToken"|sed 's/: /|/g'|sed 's/"//g'|sed 's/,$//')
do
declare -a LIST
LIST=($(echo $i|sed 's/|/ /g'))
case ${LIST[0]} in
    'AccessKeyId')
      AWS_ACCESS_KEY_ID=${LIST[1]}
    ;;
    'SecretAccessKey')
      AWS_SECRET_ACCESS_KEY=${LIST[1]}
    ;;
    'SessionToken')
      AWS_SESSION_TOKEN=${LIST[1]}
    ;;
esac
done



# remove file if exist
[[ -f ${filename} ]] && rm ${filename}



# exit if  any of the variables are missing
[[ -z ${AWS_ACCESS_KEY_ID} || -z ${AWS_SECRET_ACCESS_KEY} || -z ${AWS_SESSION_TOKEN} ]] && exit 1004


echo "unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN" > ${filename}
echo "export AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID"" >> ${filename}
echo "export AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY"" >> ${filename}
echo "export AWS_SESSION_TOKEN="$AWS_SESSION_TOKEN"" >> ${filename}
echo "export AWS_REGION="$region"" >> ${filename}
echo "source ./${filename}"
