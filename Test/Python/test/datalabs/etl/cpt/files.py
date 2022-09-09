""" source: datalabs.etl.s3.extract """
import datetime
import mock
import pytest
from   dateutil.tz import tzutc

from   datalabs.etl.cpt.files import ReleaseFilesListExtractorTask


# pylint: disable=redefined-outer-name, protected-access, invalid-name
def test_mocked_list_dir_files(parameters, object_listing):
    task = ReleaseFilesListExtractorTask(parameters)
    files = None
    with mock.patch("boto3.client") as client:
        client.return_value.list_objects_v2.return_value = object_listing

        with task._get_client() as s3:
            task._client = s3
            files = list(task._list_files("AMA/CPT/"))

        # list all files in directory AMA/CPT/
        assert len(files) == 3
        assert "20220825" in files
        assert "20220825" in files
        assert "20211112" in files


# pylint: disable=redefined-outer-name, protected-access, invalid-name
def test_mocked_get_files(parameters, object_listing):
    task = ReleaseFilesListExtractorTask(parameters)
    files = [None, None]
    with mock.patch("boto3.client") as client:
        client.return_value.list_objects_v2.return_value = object_listing
        with task._get_client() as s3:
            task._client = s3
            files = task._get_files()

        # list current&prior release zip files in directory AMA/CPT/
        assert len(files) == 2
        assert "AMA/CPT/20220825/foo.txt" in files[0]
        assert "AMA/CPT/20220824/foo.txt" in files[1]


# pylint: disable=redefined-outer-name, protected-access, invalid-name
def test_mocked_list_extract_files(parameters, object_listing):
    task = ReleaseFilesListExtractorTask(parameters)
    data = [None,None]
    with mock.patch("boto3.client") as client:
        client.return_value.list_objects_v2.return_value = object_listing
        with task._get_client() as s3:
            task._client = s3
            data = task._extract()

        # 2 files to be extracted
        assert len(data) == 2


# pylint: disable=redefined-outer-name, protected-access, invalid-name
@pytest.fixture

def parameters():
    return dict(
        BUCKET='jumanji',
        BASE_PATH='AMA/CPT',
        LINK_FILES_ZIP='foo.txt',
        EXECUTION_TIME='20220901'
            )


# pylint: disable=line-too-long
@pytest.fixture
def object_listing():
    return {'ResponseMetadata': {'RequestId': 'ESQCJTX5EGF0MNA9', 'HostId': '31z7Cwa0tgCRjKNBS06hucoN3cfzVgoB/anrjDcmZ7KgkG2Zm3aFip55Q7UigG/DWp11z8CmpLw=', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amz-id-2': '31z7Cwa0tgCRjKNBS06hucoN3cfzVgoB/anrjDcmZ7KgkG2Zm3aFip55Q7UigG/DWp11z8CmpLw=', 'x-amz-request-id': 'ESQCJTX5EGF0MNA9', 'date': 'Wed, 31 Aug 2022 18:25:24 GMT', 'x-amz-bucket-region': 'us-east-1', 'content-type': 'application/xml', 'transfer-encoding': 'chunked', 'server': 'AmazonS3'}, 'RetryAttempts': 0}, 'IsTruncated': False, 'Contents': [{'Key': 'AMA/CPT/20211112/foo.txt', 'LastModified': datetime.datetime(2021, 11, 12, 17, 29, 46, tzinfo=tzutc()), 'ETag': '"d41d8cd98f00b204e9800998ecf8427e"', 'Size': 0, 'StorageClass': 'STANDARD'}, {'Key': 'AMA/CPT/20220825/foo.txt', 'LastModified': datetime.datetime(2022, 8, 25, 15, 28, 27, tzinfo=tzutc()), 'ETag': '"beff53cfb86ba56a577298131a0907b8"', 'Size': 23, 'StorageClass': 'STANDARD'}, {'Key': 'AMA/CPT/20220824/foo.txt', 'LastModified': datetime.datetime(2022, 8, 24, 20, 56, 31, tzinfo=tzutc()), 'ETag': '"516401d00004232cc330234548ed4812"', 'Size': 70, 'StorageClass': 'STANDARD'}, {'Key': 'AMA/CPT/20211112/foo.txt', 'LastModified': datetime.datetime(2021, 11, 12, 17, 29, 46, tzinfo=tzutc()), 'ETag': '"1159a7c22f53f054d41c8ca1169d5b7c"', 'Size': 14, 'StorageClass': 'STANDARD'}], 'Name': 'ama-sbx-datalake-ingest-us-east-1', 'Prefix': 'AMA/Test/', 'MaxKeys': 1000, 'EncodingType': 'url', 'KeyCount': 4}
