""" source: datalabs.etl.s3.extract """
import datetime
from   dateutil.tz import tzutc

import mock
import pytest

from   datalabs.access.aws import AWSClient
from   datalabs.etl.cpt.files.core.extract import InputFilesListExtractorTask


# pylint: disable=redefined-outer-name, protected-access, invalid-name
def test_mocked_list_dir_files(object_listing):
    files = None

    with mock.patch("boto3.client") as client:
        client.return_value.list_objects_v2.return_value = object_listing

        with AWSClient('s3') as s3:
            files = list(InputFilesListExtractorTask._list_files(s3, "ama-abc-datalake-ingest-us-east-1", "AMA/CPT/"))

        return files

    assert len(files) == 4
    assert "20210831" in files
    assert "20210930" in files
    assert "20211230" in files
    assert "20220401" in files


# pylint: disable=redefined-outer-name, protected-access, invalid-name
def test_extract_yields_correct_input_files(parameters, object_listing):
    task = InputFilesListExtractorTask(parameters)
    data = [None,None]

    with mock.patch("boto3.client") as client:
        client.return_value.list_objects_v2.return_value = object_listing

        files = task._extract()

    assert len(files) == 4
    assert "AMA/CPT/20210831/output/internal_Property.txt" in files
    assert "AMA/CPT/20210831/output/RelationshipGroup.txt" in files
    assert "AMA/CPT/20220401/output/internal_Property.txt" in files
    assert "AMA/CPT/20220401/output/RelationshipGroup.txt" in files


# pylint: disable=redefined-outer-name, protected-access, invalid-name
@pytest.fixture
def parameters():
    return dict(
        BUCKET='ama-abc-datalake-ingest-us-east-1',
        BASE_PATH='AMA/CPT',
        EXECUTION_TIME='20220701'
    )


# pylint: disable=line-too-long
@pytest.fixture
def object_listing():
    return {
        'ResponseMetadata': {'RequestId': 'ESQCJTX5EGF0MNA9', 'HostId': '31z7Cwa0tgCRjKNBS06hucoN3cfzVgoB/anrjDcmZ7KgkG2Zm3aFip55Q7UigG/DWp11z8CmpLw=', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amz-id-2': '31z7Cwa0tgCRjKNBS06hucoN3cfzVgoB/anrjDcmZ7KgkG2Zm3aFip55Q7UigG/DWp11z8CmpLw=', 'x-amz-request-id': 'ESQCJTX5EGF0MNA9', 'date': 'Wed, 31 Aug 2022 18:25:24 GMT', 'x-amz-bucket-region': 'us-east-1', 'content-type': 'application/xml', 'transfer-encoding': 'chunked', 'server': 'AmazonS3'}, 'RetryAttempts': 0}, 'IsTruncated': False,
        'Contents': [
            {'Key': 'AMA/CPT/20210831', 'LastModified': datetime.datetime(2021, 11, 12, 17, 29, 46, tzinfo=tzutc()), 'ETag': '"d41d8cd98f00b204e9800998ecf8427e"', 'Size': 0, 'StorageClass': 'STANDARD'},
            {'Key': 'AMA/CPT/20210930', 'LastModified': datetime.datetime(2022, 8, 25, 15, 28, 27, tzinfo=tzutc()), 'ETag': '"beff53cfb86ba56a577298131a0907b8"', 'Size': 23, 'StorageClass': 'STANDARD'},
            {'Key': 'AMA/CPT/20211230', 'LastModified': datetime.datetime(2022, 8, 24, 20, 56, 31, tzinfo=tzutc()), 'ETag': '"516401d00004232cc330234548ed4812"', 'Size': 70, 'StorageClass': 'STANDARD'},
            {'Key': 'AMA/CPT/20220401', 'LastModified': datetime.datetime(2021, 11, 12, 17, 29, 46, tzinfo=tzutc()), 'ETag': '"1159a7c22f53f054d41c8ca1169d5b7c"', 'Size': 14, 'StorageClass': 'STANDARD'},
            {'Key': 'AMA/CPT/20220701', 'LastModified': datetime.datetime(2021, 11, 12, 17, 29, 46, tzinfo=tzutc()), 'ETag': '"1159a7c22f53f054d41c8ca1169d5b7c"', 'Size': 14, 'StorageClass': 'STANDARD'},
            {'Key': 'AMA/CPT/20220901', 'LastModified': datetime.datetime(2021, 11, 12, 17, 29, 46, tzinfo=tzutc()), 'ETag': '"1159a7c22f53f054d41c8ca1169d5b7c"', 'Size': 14, 'StorageClass': 'STANDARD'},
            {'Key': 'AMA/CPT/20220930', 'LastModified': datetime.datetime(2021, 11, 12, 17, 29, 46, tzinfo=tzutc()), 'ETag': '"1159a7c22f53f054d41c8ca1169d5b7c"', 'Size': 14, 'StorageClass': 'STANDARD'}
        ],
        'Name': 'ama-abc-datalake-ingest-us-east-1',
        'Prefix': 'AMA/Test/',
        'MaxKeys': 1000, 'EncodingType': 'url', 'KeyCount': 4
    }
