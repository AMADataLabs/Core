''' Simple AWS client context manager. '''
import boto3

class AWSClient:
    def __init__(self, service: str, **kwargs):
        self._service = service
        self._kwargs = kwargs
        self._client = None

    def __enter__(self):
        self._client = boto3.client(self._service, **self._kwargs)

        return self._client

    def __exit__(self, *args, **kwargs):
        self._client = None
