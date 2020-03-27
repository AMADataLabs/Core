""" Credentials collecting and error classes. """
import os
import re


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
    def load(cls, key:str):
        """ Load credentials from environment variables of the form CREDENTIALS_<KEY>_USERNAME='<username>' and CREDENTIALS_<KEY>_PASSWORD='<password>'. """
        username = cls._load_credentials_variable('USERNAME', key)
        password = cls._load_credentials_variable('PASSWORD', key)

        return Credentials(username, password)

    @classmethod
    def _load_credentials_variable(cls, type, key):
        name = f'CREDENTIALS_{type.upper()}_{key.upper()}'
        value = os.environ.get(name)

        if value is None:
            raise CredentialsError(f'Unable to load environment variable {name}.')

        return value


class CredentialsError(Error):
    pass