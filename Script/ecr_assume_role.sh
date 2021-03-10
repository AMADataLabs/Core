#!/bin/bash

profile=${1:-ecr_ecs_access}

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


for i in $(aws sts --profile $profile assume-role --role-arn "arn:aws:iam::${account}:role/ecrdeploymentrole" --role-session-name ecrpush1|egrep "AccessKeyId|SecretAccessKey|SessionToken"|sed 's/: /|/g'|sed 's/"//g'|sed 's/,$//')
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

 

filename=".ecrtoken_$(date +%Y%m%d%H%M%S)"
# remove file if exist
[[ -f ${filename} ]] && rm ${filename}

 

# exit if  any of the variables are missing
[[ -z ${AWS_ACCESS_KEY_ID} || -z ${AWS_SECRET_ACCESS_KEY} || -z ${AWS_SESSION_TOKEN} ]] && exit 1004

 
aws ecr get-login-password --region $region | docker login --username AWS --password-stdin ${AWS_REGISTRY_URL}

echo "unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN" > ${filename}
echo "export AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID"" >> ${filename}
echo "export AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY"" >> ${filename}
echo "export AWS_SESSION_TOKEN="$AWS_SESSION_TOKEN"" >> ${filename}
echo "export AWS_REGION="$region"" >> ${filename}
echo "export AWS_REGISTRY_URL="${account}.dkr.ecr.${region}.amazonaws.com"" >> ${filename}
echo "source ./${filename}"
