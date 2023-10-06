""" source: datalabs.etl.dynamodb.load """
import mock
import pytest

from   datalabs.etl.cpt.vignettes.load import DynamoDBLoaderTask


@pytest.mark.skip(reason="Need data from database")
# pylint: disable=redefined-outer-name, protected-access
def test_dynamodb_loader():
    data = '[{"pk": "foo", "sk": "bar"}]'
    data = data.encode('utf-8')

    with mock.patch('boto3.client'):
        task = DynamoDBLoaderTask(parameters={}, data=[data])
        task.run()


# pylint: disable=protected-access
def test_create_hash_entries():
    data = [
        {
            "pk": "CPT CODE:1234",
            "sk": "CONCEPT:0987",
            "typical_patient": "FOO",
            "pre_service_info": "nan",
            "intra_service_info": "BAR",
            "post_service_info": "nan",
            "ruc_reviewed_date": "nan"
        },
        {
            "pk": "CPT CODE:5678",
            "sk": "CONCEPT:6543",
            "typical_patient": "FOO",
            "pre_service_info": "nan",
            "intra_service_info": "BAR",
            "post_service_info": "nan",
            "ruc_reviewed_date": "nan"
        }
    ]
    expected_output = [
        {
            "pk": "CPT CODE:1234",
            "sk": "CONCEPT:0987",
            "typical_patient": "FOO",
            "pre_service_info": "nan",
            "intra_service_info": "BAR",
            "post_service_info": "nan",
            "ruc_reviewed_date": "nan",
            "md5": "49e540db99ee272aeb777b234db84854"
        },
        {
            "pk": "CPT CODE:5678",
            "sk": "CONCEPT:6543",
            "typical_patient": "FOO",
            "pre_service_info": "nan",
            "intra_service_info": "BAR",
            "post_service_info": "nan",
            "ruc_reviewed_date": "nan",
            "md5": "00275cbc68c02e2930907f4628942c0e"
        }
    ]

    output = DynamoDBLoaderTask._create_hash_entries(data)

    assert output.to_dict('records') == expected_output
