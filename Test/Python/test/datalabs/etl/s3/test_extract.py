""" source: datalabs.etl.s3.extract """
import datetime
from   io import BytesIO
import itertools
import os
import os.path
import mock
import pytest
from   dateutil.tz import tzutc

from   botocore.response import StreamingBody
import pandas

from   datalabs.access.aws import AWSClient
from   datalabs.etl.s3.extract import S3FileExtractorTask, S3FileExtractorParameters, S3WindowsTextFileExtractorTask


# pylint: disable=redefined-outer-name, protected-access
def test_parameters_are_deserialized(parameters):
    with mock.patch('boto3.client'):
        task = S3FileExtractorTask(parameters)

        assert isinstance(task._parameters, S3FileExtractorParameters)


# pylint: disable=redefined-outer-name, protected-access
def test_whitespace_removed_from_filenames(parameters):
    with mock.patch('boto3.client'):
        task = S3FileExtractorTask(parameters)

        files = task._get_files()

        assert len(files) == 3
        assert files[2] == 'dir1/dir2/dir3/19000101/the_other_one.csv'


# pylint: disable=redefined-outer-name, protected-access
def test_files_parsed_from_data():
    data = [b"foo.txt\nbar.txt"]
    files = list(itertools.chain.from_iterable(S3FileExtractorTask._parse_file_lists(data, False)))

    assert len(files) == 2
    for name, expected_name in zip(files, ["foo.txt", "bar.txt"]):
        assert name == expected_name


# pylint: disable=redefined-outer-name, protected-access
def test_header_parsed_from_data_is_ignored():
    data = [b"filename\nfoo.txt\nbar.txt"]
    files = list(itertools.chain.from_iterable(S3FileExtractorTask._parse_file_lists(data, True)))

    assert len(files) == 2
    for name, expected_name in zip(files, ["foo.txt", "bar.txt"]):
        assert name == expected_name

# pylint: disable=redefined-outer-name, protected-access
def test_disabling_datestamp_works(parameters):
    with mock.patch('boto3.client'):
        parameters['INCLUDE_DATESTAMP'] = 'false'
        task = S3FileExtractorTask(parameters)

        files = task._get_files()

        assert len(files) == 3
        assert files[2] == 'dir1/dir2/dir3/the_other_one.csv'


# pylint: disable=redefined-outer-name, protected-access
def test_datetime_formatting_in_base_path_works(parameters):
    with mock.patch('boto3.client'):
        parameters['INCLUDE_DATESTAMP'] = 'false'
        parameters['BASE_PATH'] = 'dir1/%Y%m%d/dir2/dir3'
        task = S3FileExtractorTask(parameters)

        files = task._get_files()
        resolved_files = task._resolve_files(files)

        assert len(resolved_files) == 3
        assert resolved_files[2] == 'dir1/19000101/dir2/dir3/the_other_one.csv'


# pylint: disable=redefined-outer-name, protected-access
def test_datetime_formatting_in_file_works(parameters):
    with mock.patch('boto3.client'):
        parameters['INCLUDE_DATESTAMP'] = 'false'
        parameters['FILES'] = 'this_one.csv,that_one.csv,\n       the_other_%Y%m%d_one.csv     '
        task = S3FileExtractorTask(parameters)

        files = task._get_files()
        resolved_files = task._resolve_files(files)

        assert len(resolved_files) == 3
        assert resolved_files[2] == 'dir1/dir2/dir3/the_other_19000101_one.csv'


# pylint: disable=redefined-outer-name, protected-access
def test_no_leading_slash_with_empty_base_path(parameters):
    with mock.patch('boto3.client'):
        parameters['BASE_PATH'] = ''
        parameters['INCLUDE_DATESTAMP'] = 'true'
        parameters['FILES'] = 'this_one.csv'
        task = S3FileExtractorTask(parameters)

        files = task._get_files()

        assert len(files) == 1
        assert files[0] == '19000101/this_one.csv'


# pylint: disable=redefined-outer-name, protected-access
def test_caching_data_to_disk(body, parameters):
    task = S3FileExtractorTask(parameters)

    path = task._cache_data_to_disk(body)

    assert os.path.isfile(path)

    data = pandas.read_csv(path)

    assert data.columns.to_list() == ['name', 'id']
    assert len(data) == 3

    os.remove(path)


def test_cp1252_decoding(parameters):
    task = S3WindowsTextFileExtractorTask(parameters)
    cp1252_encoded_text = '¥'.encode('cp1252')
    unicode_encoded_text = task._decode_data(cp1252_encoded_text)

    assert unicode_encoded_text == '¥'.encode("utf-8")


# pylint: disable=redefined-outer-name, protected-access
def test_missing_filenames(parameters):
    parameters.pop("FILES")
    task = S3FileExtractorTask(parameters)

    with pytest.raises(ValueError):
        task._get_files()


# pylint: disable=redefined-outer-name, protected-access
def test_filenames_in_data(parameters, data):
    parameters.pop("FILES")

    task = S3FileExtractorTask(parameters, data)

    files = task._get_files()

    assert len(files) == 3


# pylint: disable=redefined-outer-name, protected-access, invalid-name
@pytest.mark.skip(reason="exploratory")
def test_print_example_object_listing():
    with AWSClient("s3") as s3:
        response = s3.list_objects_v2(Bucket="ama-sbx-datalake-ingest-us-east-1", Prefix="AMA/Test/")

    print(response)
    assert False


# pylint: disable=redefined-outer-name, protected-access, invalid-name
def test_mocked_list_objects_v2_output_is_returned_by_list_files(parameters, data, object_listing):
    parameters.pop("FILES")

    task = S3FileExtractorTask(parameters, data)
    files = None

    with mock.patch("boto3.client") as client:
        client.return_value.list_objects_v2.return_value = object_listing

        with task._get_client() as s3:
            task._client = s3

            files = list(task._list_files("does/not/matter/"))

    assert len(files) == 3
    assert "20220825" in files
    assert "40960816" in files
    assert "foo.txt" in files


@pytest.fixture
def parameters():
    return dict(
        ENDPOINT_URL='https://bogus.host.fqdn/path/file',
        ACCESS_KEY='nviowaj4902hfisafh9402fdni0ph8',
        SECRET_KEY='wr9e0afe90afohf90aw',
        REGION_NAME='us-east-42',
        BUCKET='jumanji',
        BASE_PATH='dir1/dir2/dir3',
        FILES='this_one.csv,that_one.csv,\n       the_other_one.csv     ',
        EXECUTION_TIME='19000101'
    )


@pytest.fixture
def body():
    data = \
b'''name,id
foo,12345
bar,54321
ping,24680
'''

    return StreamingBody(BytesIO(data), len(data))


@pytest.fixture
def data():
    return [
        """this_one.csv
        that_one.csv   """.encode(),
        'the_other_one.csv'.encode()
    ]

# pylint: disable=line-too-long
@pytest.fixture
def object_listing():
    return {'ResponseMetadata': {'RequestId': 'ESQCJTX5EGF0MNA9', 'HostId': '31z7Cwa0tgCRjKNBS06hucoN3cfzVgoB/anrjDcmZ7KgkG2Zm3aFip55Q7UigG/DWp11z8CmpLw=', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amz-id-2': '31z7Cwa0tgCRjKNBS06hucoN3cfzVgoB/anrjDcmZ7KgkG2Zm3aFip55Q7UigG/DWp11z8CmpLw=', 'x-amz-request-id': 'ESQCJTX5EGF0MNA9', 'date': 'Wed, 31 Aug 2022 18:25:24 GMT', 'x-amz-bucket-region': 'us-east-1', 'content-type': 'application/xml', 'transfer-encoding': 'chunked', 'server': 'AmazonS3'}, 'RetryAttempts': 0}, 'IsTruncated': False, 'Contents': [{'Key': 'AMA/Test/', 'LastModified': datetime.datetime(2021, 11, 12, 17, 29, 46, tzinfo=tzutc()), 'ETag': '"d41d8cd98f00b204e9800998ecf8427e"', 'Size': 0, 'StorageClass': 'STANDARD'}, {'Key': 'AMA/Test/20220825/hello_world_message.txt', 'LastModified': datetime.datetime(2022, 8, 25, 15, 28, 27, tzinfo=tzutc()), 'ETag': '"beff53cfb86ba56a577298131a0907b8"', 'Size': 23, 'StorageClass': 'STANDARD'}, {'Key': 'AMA/Test/40960816/s3_file_loader_task_tests.txt', 'LastModified': datetime.datetime(2022, 8, 24, 20, 56, 31, tzinfo=tzutc()), 'ETag': '"516401d00004232cc330234548ed4812"', 'Size': 70, 'StorageClass': 'STANDARD'}, {'Key': 'AMA/Test/foo.txt', 'LastModified': datetime.datetime(2021, 11, 12, 17, 29, 46, tzinfo=tzutc()), 'ETag': '"1159a7c22f53f054d41c8ca1169d5b7c"', 'Size': 14, 'StorageClass': 'STANDARD'}], 'Name': 'ama-sbx-datalake-ingest-us-east-1', 'Prefix': 'AMA/Test/', 'MaxKeys': 1000, 'EncodingType': 'url', 'KeyCount': 4}
