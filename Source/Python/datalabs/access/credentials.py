""" Credentials collecting and error classes. """

import os


class Credentials():
    def __init__(self, username, password):
        self.__username = username
        self.__password = password

    @property
    def username(self):
        return self.__username

    @property
    def password(self):
        return self.__password

    @classmethod
    def load(cls, key: str):
        """ Load credentials from environment variables.
            Variables are of the form CREDENTIALS_<KEY>_USERNAME='<username>' and
            CREDENTIALS_<KEY>_PASSWORD='<password>'.
        """
        username = cls._load_credentials_variable(key, 'USERNAME')
        password = cls._load_credentials_variable(key, 'PASSWORD')

        return Credentials(username, password)

    @classmethod
    def _load_credentials_variable(cls, key, credential_type):
        name = f'CREDENTIALS_{key.upper()}_{credential_type.upper()}'
        value = os.environ.get(name)

        if value is None:
            raise CredentialsException(f'Unable to load environment variable {name}.')

        return value


class CredentialsException(Exception):
    pass