""" source: datalabs.etl.dynamodb.load """
import logging

import mock
import pytest

from   collections import defaultdict

from   datalabs.etl.dynamodb.load import DynamoDBLoaderTask


@pytest.mark.skip(reason="Need data from database")
# pylint: disable=redefined-outer-name, protected-access
def test_dynamodb_loader():
    data = '[{"pk": "foo", "sk": "bar"}]'
    data = data.encode('utf-8')

    with mock.patch('boto3.client'):
        task = DynamoDBLoaderTask(parameters=dict(), data=[data])
        task.run()


def test_create_hash_entries():
    data = [{"pk": "foo", "sk": "UNMAPPABLE:12345"}, {"pk": "bar", "sk": "CPT:67890"}]
    expected_output = [{"pk": "foo:UNMAPPABLE:12345", "sk": "MD5:efe1007947cb225e744645007619502b"},
                       {"pk": "bar:CPT:67890", "sk": "MD5:ce888b0c37f85f28900ec49a473bed13"}]

    output = DynamoDBLoaderTask._create_hash_entries(data)

    assert output.to_dict('records') == expected_output



