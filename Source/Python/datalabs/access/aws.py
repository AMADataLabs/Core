''' Simple AWS client context manager. '''
import boto3

class AWSClient:
    def __init__(self, service: str, **kwargs):
        self._service = service
        self._kwargs = kwargs
        self._client = None

    def __enter__(self):
        aws_environment = self._kwargs.pop("aws_environment")
        if aws_environment is not None:
            self._assume_new_role(aws_environment)

        self._client = boto3.client(self._service, **self._kwargs)

        return self._client

    def __exit__(self, *args, **kwargs):
        self._client = None

    def _assume_new_role(self, aws_environment):
        environment_account_mapping = {
            'dev': '191296302136',
            'tst': '194221139997',
            'stg': '340826698851',
            'prd': '285887636563'
        }
        try:
            account = environment_account_mapping[aws_environment]
        except KeyError as exception:
            raise KeyError("aws_environment must be one of 'dev', 'tst', 'stg' or 'prd'") from exception

        sts_client = boto3.client('sts', **self._kwargs)
        assumed_role_object=sts_client.assume_role(
            RoleArn=f"arn:aws:iam::{account}:role/{aws_environment}"\
            "-ama-apigateway-invoke-role",
            RoleSessionName="datalabs"
        )
        credentials=assumed_role_object['Credentials']

        self._kwargs["aws_session_token"] = credentials["SessionToken"]
        self._kwargs["aws_secret_access_key"] = credentials["SecretAccessKey"]
        self._kwargs["aws_access_key_id"] = credentials["AccessKeyId"]
