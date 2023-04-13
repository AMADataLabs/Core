''' Simple AWS client context manager. '''
import os

import boto3

class AWSClient:
    def __init__(self, service: str, **kwargs):
        self._service = service
        self._kwargs = kwargs
        self._client = None
        self._ssl_verification = True
        self._client_factory = boto3.client

        if os.getenv('AWS_NO_VERIFY_SSL') == "True":
            self._ssl_verification = False

    @property
    def resource(self):
        aws_client = AWSClient(self._service, **self._kwargs)
        aws_client._client_factory = boto3.resource

        return aws_client

    def __enter__(self):
        assume_role = self._kwargs.pop("assume_role", None)
        profile = self._kwargs.pop("profile", None)

        if assume_role is not None:
            role = self._assume_role(assume_role, profile=profile)

            self._kwargs.update(self._get_credential_kwargs(role["Credentials"]))

        self._client = self._client_factory(self._service, verify=self._ssl_verification, **self._kwargs)

        return self._client

    def __exit__(self, *args, **kwargs):
        self._client = None

    def _assume_role(self, assume_role, profile=None):
        session = boto3.session.Session(profile_name=profile)
        sts_client = session.client('sts', verify=self._ssl_verification, **self._kwargs)

        return sts_client.assume_role(
            RoleArn=assume_role,
            RoleSessionName="datalabs"
        )

    @classmethod
    def _get_credential_kwargs(cls, credentials):
        return dict(
            aws_session_token=credentials["SessionToken"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_access_key_id=credentials["AccessKeyId"]
        )
