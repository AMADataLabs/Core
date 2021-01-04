""" Generic database object intended to be subclassed by specific databases. """
from abc import ABC, abstractmethod

import datalabs.access.credentials as cred


class Datastore(ABC):
    def __init__(self, credentials: cred.Credentials = None, key: str = None):
        self._key = key or self.__class__.__name__.upper()
        self._credentials = self._load_or_verify_credentials(credentials, self._key)
        self._connection = None

    def __enter__(self):
        self.connect()

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    @abstractmethod
    def connect(self):
        return self._connection

    def close(self):
        self._connection.close()

        self._connection = None

    @classmethod
    def _load_or_verify_credentials(cls, credentials: cred.Credentials, key: str):
        if credentials is None:
            credentials = cred.Credentials.load(key)
        elif not hasattr(credentials, 'username') or not hasattr(credentials, 'password'):
            raise ValueError('Invalid credentials object.')

        return credentials
