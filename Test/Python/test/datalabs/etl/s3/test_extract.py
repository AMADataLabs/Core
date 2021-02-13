""" source: datalabs.etl.s3.extract """
import mock
import pytest

import datalabs.etl.s3.extract as s3
import datalabs.etl.task as etl


# pylint: disable=redefined-outer-name, protected-access
def test_parameters_are_deserialized(parameters):
    with mock.patch('boto3.client'):
        task = s3.S3FileExtractorTask(parameters)

        assert isinstance(task._parameters, s3.S3FileExtractorParameters)


@pytest.fixture
def parameters():
    return etl.ETLComponentParameters(
        variables=dict(
            ENDPOINT_URL='https://bogus.host.fqdn/path/file',
            ACCESS_KEY='nviowaj4902hfisafh9402fdni0ph8',
            SECRET_KEY='wr9e0afe90afohf90aw',
            REGION_NAME='us-east-42',
            BUCKET='jumanji',
            BASE_PATH='dir1/dir2/dir3',
            FILES='this_one.csv,that_one.csv,the_other_one.csv',
            EXECUTION_TIME='19000101'
        )
    )
