#!/bin/bash

profile=dataroom
account=644454719059
region=us-east-1

unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN


for i in $(aws sts --profile ${profile} assume-role --role-arn "arn:aws:iam::${account}:role/DataRoom-automation" --role-session-name datalabs | egrep "AccessKeyId|SecretAccessKey|SessionToken"|sed 's/: /|/g'|sed 's/"//g'|sed 's/,$//')
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



filename=".dataroom_token_$(date +%Y%m%d%H%M%S)"
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
