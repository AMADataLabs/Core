import argparse

from   datalabs.access.aws import AWSClient


ACCOUNTS = dict(
    dev="191296302136",
    tst="194221139997",
    stg="340826698851",
    prd="285887636563",
    shr="394406051370"
)


ROLES = dict(
    apigw=""
)


def main(args):
    role = None

    if args["role"] == "ecr":
        args["environment"] = "shr"

    role_arn = get_role_arn(args["role"], args["environment"])

    role = assume_role(role_arn, profile=args["role"])

    credentials = role["Credentials"]

    print(" ".join((credentials["AccessKeyId"], credentials["SecretAccessKey"], credentials["SessionToken"]))


def get_role_arn(role, environment):
    account = ACCOUNTS[environment]
    arn = None

    if role == "apigw":
        arn = f"arn:aws:iam::{account}:role/{environment}-ama-apigateway-invoke-role"
    elif role == "ecs":
        arn = f"arn:aws:iam::{account}:role/ama-ecs-task-deployment"
    elif role == "ecr":
        arn = f"arn:aws:iam::{account}:role/ecrdeploymentrole"


def assume_role(self, assume_role, profile):
    session = boto3.session.Session(profile_name=profile)
    sts_client = session.client('sts', verify=self._ssl_verification, **self._kwargs)

    return sts_client.assume_role(
        RoleArn=assume_role,
        RoleSessionName="datalabs"
    )


if __name__ == '__main__':
    return_code = 0

    ap = argparse.ArgumentParser()
    ap.add_argument('-r', '--role', help='Role alias. One of "apigw", "ecs", or "ecr".')
    )
    ap.add_argument(
        '-e', '--environment', default="",
        help='AWS environment ID. One of "dev", "tst", "stg", or "prd"'
    )
    args = vars(ap.parse_args())

    try:
        main(args)
    except Exception as e:
        LOGGER.exception("Failed to create project bundle.")
        return_code = 1

    exit(return_code)
