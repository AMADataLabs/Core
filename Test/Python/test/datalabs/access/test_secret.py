""" AWS Secrets Manager access tests """
from   datetime import datetime
import json
import os

import boto3
import mock
import pytest

from   datalabs.access.secret import SecretsManagerEnvironmentLoader


# pylint: disable=redefined-outer-name
def test_get_secrets_from_secret_store(secret_values):
    with mock.patch('datalabs.access.secret.boto3') as mock_boto3:
        mock_boto3.client.return_value.get_secret_value.return_value = secret_values

        loader = SecretsManagerEnvironmentLoader(
            {
                'DATABASE_FOOBAR_SECRET': 'DataLabs/FooBar/RDS/secret',
            }
        )
        loader.load()

        assert 'DATABASE_FOOBAR_SECRET' in os.environ
        secret = json.loads(os.getenv("DATABASE_FOOBAR_SECRET"))
        assert len(secret) == 6
        assert "dbinstanceIdentifier" in secret
        assert "dbname" in secret
        assert "engine" in secret
        assert "port" in secret
        assert "username" in secret
        assert "password" in secret


# pylint: disable=redefined-outer-name, protected-access, unused-argument
def test_from_environ(environment):
    with mock.patch('datalabs.access.secret.boto3'):
        loader = SecretsManagerEnvironmentLoader.from_environ()
        values = loader._secrets.values()

    assert 'DATABASE_FOOBAR_SECRET' in loader._secrets
    assert 'DataLabs/FooBar/RDS/secret' in values


@pytest.mark.skip(reason="Example Boto3 Usage")
def test_boto3_get_secret_value():
    secrets_manager = boto3.client('secretsmanager', verify=False)

    response = secrets_manager.get_secret_value(SecretId='DataLabs/CPT/API/database')
    print(response)

    secret = json.loads(response["SecretString"])
    assert len(secret) == 6
    assert "dbinstanceIdentifier" in secret
    assert "dbname" in secret
    assert "engine" in secret
    assert "port" in secret
    assert "username" in secret
    assert "password" in secret

    print(secret)
    assert False


@pytest.fixture
def secret_values():
    return {
        "ARN": "arn:aws:secretsmanager:us-east-1:644454719059:secret:DataLabs/FooBar/RDS/secret-a9b74h",
        "CreatedDate": datetime(2020, 12, 7, 10, 36, 55, 622000),
        "Name": "DataLabs/FooBar/RDS/secret",
        "SecretString": '{"dbinstanceIdentifier":"my-rds-instance","dbname":"mydatabase","engine":"postgres",'
                        '"password":"ligo123","port":5432,"username":"mrtwinkles"}',
        "VersionId": "E3307904-343D-4DA7-BC63-86F4B67AC018",
        "VersionStages": ['AWSCURRENT']
    }


@pytest.fixture
def environment():
    current_environment = os.environ.copy()

    os.environ['DATABASE_FOOBAR_SECRET'] \
        = 'arn:aws:secretsmanager:us-east-1:644454719059:secret/DataLabs/FooBar/RDS/secret'

    yield os.environ

    os.environ.clear()
    os.environ.update(current_environment)
