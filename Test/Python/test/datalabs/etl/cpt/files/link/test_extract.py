""" source: datalabs.etl.s3.extract """
# pylint: disable=invalid-name
import datetime
from   dateutil.tz import tzutc

import mock
import pytest

from   datalabs.access.aws import AWSClient
from   datalabs.etl.cpt.files.link.extract import InputFilesListExtractorTask


def _get_client():
    return AWSClient('s3')

### Fix unit test ###
# pylint: disable=redefined-outer-name, protected-access, invalid-name
def test_mocked_list_dir_files(parameters, object_listing):
    task = InputFilesListExtractorTask(parameters)
    files = None

    with mock.patch("boto3.client") as client:
        client.return_value.list_objects_v2.return_value = object_listing

        def _list_release_folders(task, files):
            with AWSClient('s3') as s3:
                files = list(task._list_files(s3, parameters['BUCKET'] ,"AMA/CPT/"))

            return files

        files = _list_release_folders(task, files)

    assert len(files) == 3
    assert "20220825" in files
    assert "20220824" in files
    assert "20210830" in files


# pylint: disable=redefined-outer-name, protected-access, invalid-name
def test_link_builder_input_files_are_correctly_identified(parameters, object_listing):
    """ Test for 2022-08-25 (Annual 2023) distribution """
    task = InputFilesListExtractorTask(parameters)
    files = []

    with mock.patch("boto3.client") as client:
        client.return_value.list_objects_v2.return_value = object_listing

        def _get_input_files(task, files):
            with AWSClient('s3') as s3:
                files = task._get_files(s3)

            return files

        files = _get_input_files(task, files)

    assert len(files) == 17

    _assert_prior_link_files_are_included(files)

    _assert_annual_files_are_included(files)

    _assert_core_files_are_included(files)


def _assert_prior_link_files_are_included(files):
    assert "AMA/CPT/20220824/output/changes/History.txt" in files
    assert "AMA/CPT/20220824/output/changes/HistoryModifers.txt" in files
    assert "AMA/CPT/20220824/output/changes/HistoryReference.txt" in files
    assert "AMA/CPT/20220824/output/changes/RenumberedCodesCitationsCrosswalk.txt" in files
    assert "AMA/CPT/20220824/output/changes/RenumberedCodesCitationsCrosswalkDescriptors.txt" in files
    assert "AMA/CPT/20220824/output/internal_Property.txt" in files
    assert "AMA/CPT/20220824/output/RelationshipGroup.txt" in files


def _assert_annual_files_are_included(files):
    assert "AMA/CPT/20210830/output/changes/History.txt" in files
    assert "AMA/CPT/20210830/output/changes/HistoryModifers.txt" in files
    assert "AMA/CPT/20210830/output/changes/HistoryReference.txt" in files
    assert "AMA/CPT/20210830/output/changes/RenumberedCodesCitationsCrosswalk.txt" in files
    assert "AMA/CPT/20210830/output/changes/RenumberedCodesCitationsCrosswalkDescriptors.txt" in files
    assert "AMA/CPT/20210830/output/internal_Property.txt" in files
    assert "AMA/CPT/20210830/output/RelationshipGroup.txt" in files


def _assert_core_files_are_included(files):
    assert "AMA/CPT/20220825/output/internal_Property.txt" in files
    assert "AMA/CPT/20220825/output/internal_Type.txt" in files
    assert "AMA/CPT/20220825/output/RelationshipGroup.txt" in files


# pylint: disable=redefined-outer-name, protected-access, invalid-name
@pytest.fixture
def parameters():
    return dict(
        BUCKET='jumanji',
        BASE_PATH='AMA/CPT',
        EXECUTION_TIME='20220825'
    )


# pylint: disable=line-too-long
@pytest.fixture
def object_listing():
    return {
        'ResponseMetadata': {'RequestId': 'ESQCJTX5EGF0MNA9', 'HostId': '31z7Cwa0tgCRjKNBS06hucoN3cfzVgoB/anrjDcmZ7KgkG2Zm3aFip55Q7UigG/DWp11z8CmpLw=', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amz-id-2': '31z7Cwa0tgCRjKNBS06hucoN3cfzVgoB/anrjDcmZ7KgkG2Zm3aFip55Q7UigG/DWp11z8CmpLw=', 'x-amz-request-id': 'ESQCJTX5EGF0MNA9', 'date': 'Wed, 31 Aug 2022 18:25:24 GMT', 'x-amz-bucket-region': 'us-east-1', 'content-type': 'application/xml', 'transfer-encoding': 'chunked', 'server': 'AmazonS3'}, 'RetryAttempts': 0}, 'IsTruncated': False,
        'Contents': [
            {'Key': 'AMA/CPT/20210830/foo.txt', 'LastModified': datetime.datetime(2021, 11, 12, 17, 29, 46, tzinfo=tzutc()), 'ETag': '"d41d8cd98f00b204e9800998ecf8427e"', 'Size': 0, 'StorageClass': 'STANDARD'},
            {'Key': 'AMA/CPT/20220825/foo.txt', 'LastModified': datetime.datetime(2022, 8, 25, 15, 28, 27, tzinfo=tzutc()), 'ETag': '"beff53cfb86ba56a577298131a0907b8"', 'Size': 23, 'StorageClass': 'STANDARD'},
            {'Key': 'AMA/CPT/20220824/foo.txt', 'LastModified': datetime.datetime(2022, 8, 24, 20, 56, 31, tzinfo=tzutc()), 'ETag': '"516401d00004232cc330234548ed4812"', 'Size': 70, 'StorageClass': 'STANDARD'}
        ],
        'Name': 'ama-sbx-datalake-ingest-us-east-1',
        'Prefix': 'AMA/Test/',
        'MaxKeys': 1000, 'EncodingType': 'url', 'KeyCount': 4
    }
