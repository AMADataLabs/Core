#!/usr/bin/env bash

profile=${1:-shared}
filename=".ecr_token_${environment}_$(date +%Y%m%d%H%M%S)"
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

account=394406051370
region=$(aws configure get ${profile}.region)

echo "Profile: $profile"
echo "Account: $account ($region)"

unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN


for i in $(aws sts ${no_verify_ssl} --profile $profile assume-role --role-arn "arn:aws:iam::${account}:role/ecrdeploymentrole" --role-session-name ecrpush1|egrep "AccessKeyId|SecretAccessKey|SessionToken"|sed 's/: /|/g'|sed 's/"//g'|sed 's/,$//')
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

 
aws_registry_url="${account}.dkr.ecr.${region}.amazonaws.com"

echo "unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN" > ${filename}
echo "export AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID"" >> ${filename}
echo "export AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY"" >> ${filename}
echo "export AWS_SESSION_TOKEN="$AWS_SESSION_TOKEN"" >> ${filename}
echo "export AWS_REGION="$region"" >> ${filename}
echo "export AWS_REGISTRY_URL="${aws_registry_url}"" >> ${filename}
echo "source ./${filename}"
echo "aws ecr get-login-password --region $region | docker login --username AWS --password-stdin ${aws_registry_url}"
