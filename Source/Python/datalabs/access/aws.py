''' Simple AWS client context manager. '''
import boto3

class AWSClient:
    def __init__(self, service: str, **kwargs):
        self._service = service
        self._kwargs = kwargs
        self._client = None

    def __enter__(self):
        assume_role = self._kwargs.pop("assume_role", None)
        if assume_role is not None:
            self._assume_new_role(assume_role)

        self._client = boto3.client(self._service, **self._kwargs)

        return self._client

    def __exit__(self, *args, **kwargs):
        self._client = None

    def _assume_new_role(self, assume_role):

        sts_client = boto3.client('sts', **self._kwargs)
        assumed_role_object=sts_client.assume_role(
            RoleArn=assume_role,
            RoleSessionName="datalabs"
        )
        credentials=assumed_role_object['Credentials']

        self._kwargs["aws_session_token"] = credentials["SessionToken"]
        self._kwargs["aws_secret_access_key"] = credentials["SecretAccessKey"]
        self._kwargs["aws_access_key_id"] = credentials["AccessKeyId"]
