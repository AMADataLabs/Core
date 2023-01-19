''' Simple AWS client context manager. '''
import os

import boto3

class AWSClient:
    def __init__(self, service: str, **kwargs):
        self._service = service
        self._kwargs = kwargs
        self._client = None
        self._ssl_verification = True

        if os.getenv('AWS_NO_VERIFY_SSL') == "True":
            self._ssl_verification = False

    def __enter__(self):
        assume_role = self._kwargs.pop("assume_role", None)
        profile = self._kwargs.pop("profile", None)

        if assume_role is not None:
            role = self._assume_role(assume_role, profile=profile)

            self._kwargs.update(self._get_credential_kwargs(role["Credentials"]))

        self._client = boto3.client(self._service, verify=self._ssl_verification, **self._kwargs)

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
    def _get_credential_kwargs(self, credentials):
        return dict(
            aws_session_token=credentials["SessionToken"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_access_key_id=credentials["AccessKeyId"]
        )
