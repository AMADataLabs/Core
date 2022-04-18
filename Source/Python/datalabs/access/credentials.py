""" Credentials collecting and error classes. """
from   dataclasses import dataclass
import os


@dataclass
class Credentials:
    username: str
    password: str

    @classmethod
    def load(cls, key: str):
        """ Load credentials from environment variables.
            Variables are of the form CREDENTIALS_<KEY>_USERNAME='<username>' and
            CREDENTIALS_<KEY>_PASSWORD='<password>'.
        """
        username = cls._load_variable(key, 'USERNAME')
        password = cls._load_variable(key, 'PASSWORD')

        return Credentials(username=username, password=password)

    @classmethod
    def _load_variable(cls, key, credential_type):
        name = f'CREDENTIALS_{key.upper()}_{credential_type.upper()}'
        value = os.environ.get(name)

        if value is None:
            raise CredentialsException(f'Unable to load environment variable {name}.')

        return value


class CredentialsException(Exception):
    pass
