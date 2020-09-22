from   datetime import datetime
import os

import boto3
import mock
import pytest

from   datalabs.access.parameter import ParameterStoreEnvironmentLoader


def test_get_parameters_from_parameter_store(parameter_values):
    with mock.patch('datalabs.access.parameter.boto3') as mock_boto3:
        mock_boto3.client.return_value.get_parameters.return_value = parameter_values

        loader =  ParameterStoreEnvironmentLoader(
            {
                '/DataLabs/FooBar/RDS/username': 'DATABASE_FOOBAR_USERNAME',
                '/DataLabs/FooBar/RDS/password': 'DATABASE_FOOBAR_PASSWORD'
            }
        )
        loader.load()

        assert 'DATABASE_FOOBAR_USERNAME' in os.environ
        assert 'DATABASE_FOOBAR_PASSWORD' in os.environ
        assert os.getenv('DATABASE_FOOBAR_USERNAME') == 'mrtwinkles'
        assert os.getenv('DATABASE_FOOBAR_PASSWORD') == 'ligo123'


@pytest.mark.skip(reason="Example Boto3 Usage")
def test_boto3_get_secure_string():
    ssm = boto3.client('ssm', verify=False)

    response = ssm.get_parameters(
        Names=[
            '/DataLabs/CPT/RDS/username',
            '/DataLabs/CPT/RDS/password',
        ],
        WithDecryption=True,
    )
    print(response)

    parameters = {parameter['Name']:parameter['Value'] for parameter in response['Parameters']}
    assert len(parameters) == 2

    print(parameters)
    assert False


@pytest.fixture
def parameter_values():
    return {
        'Parameters': [
            {
                'Name': '/DataLabs/FooBar/RDS/username',
                'Type': 'String',
                'Value': 'mrtwinkles',
                'Version': 6,
                'LastModifiedDate': datetime(2015, 1, 1),
                'ARN': 'arn:aws:ssm:us-east-1:644454719059:parameter/DataLabs/CPT/FooBar/username',
            },
            {
                'Name': '/DataLabs/FooBar/RDS/password',
                'Type': 'SecureString',
                'Value': 'ligo123',
                'Version': 4,
                'LastModifiedDate': datetime(2016, 10, 22),
                'ARN': 'arn:aws:ssm:us-east-1:644454719059:parameter/DataLabs/CPT/FooBar/password',
            },
        ],
        'InvalidParameters': []
    }
