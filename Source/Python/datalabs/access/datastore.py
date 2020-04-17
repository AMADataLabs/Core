""" Generic database object intended to be subclassed by specific databases. """
from abc import ABC, abstractmethod

import datalabs.access.credentials as cred


class Datastore(ABC):
    def __init__(self, credentials: cred.Credentials = None):
        self._key = self.__class__.__name__.upper()
        self._credentials = self._load_credentials(credentials, self._key)
        self._connection = None

    def __enter__(self):
        self.connect()

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    @abstractmethod
    def connect(self):
        self._connection = None

    def close(self):
        self._connection.close()

    @classmethod
    def _load_credentials(cls, credentials: cred.Credentials, key: str):
        if credentials is None:
            credentials = cred.Credentials.load(key)
        elif not hasattr(credentials, 'username') or hasattr(credentials, 'password'):
            raise ValueError('Invalid credentials object.')

        return credentials
