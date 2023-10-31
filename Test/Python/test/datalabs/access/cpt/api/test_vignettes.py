""" source: datalabs.access.cpt.api.vignettes """
import pytest
import mock

from   datalabs.access.cpt.api.vignettes import VignetteLookupEndpointTask


# pylint: disable=redefined-outer-name, protected-access
def test_get_mappings_for_code(test_event, test_data):
    with mock.patch('datalabs.access.cpt.api.vignettes.AWSClient') as mock_aws_client:
        mock_result = mock_aws_client().__enter__().execute_statement.return_value

        mock_result.__getitem__.return_value = test_data

        task = VignetteLookupEndpointTask(test_event)

        results = task._get_mappings_for_code("99202")

        assert results["Items"][0]["pk"] == "CPT CODE:99202"

def test_generate_response(test_event, mappings):
    task = VignetteLookupEndpointTask(test_event)

    results = task._generate_response(mappings)

    assert results["cpt_code"] == "123"
    assert results["typical_patient"] == "Patient Info"

def test_generate_response_no_additional_info(test_event, mappings):
    test_event['query'] = {"additional_information": ["FALSE"]}

    task = VignetteLookupEndpointTask(test_event)
    results = task._generate_response(mappings)

    assert results["cpt_code"] == "123"
    assert 'concept_id' not in results

@pytest.fixture
def test_event():
    return dict(
        method="GET",
        path={"cpt_code": "99202"},
        query={"additional_information": ["TRUE"]},
        authorization={"token": "your_token"},
        database_table="YourDatabaseTable",
        unknowns={"key1": "value1"}
    )

@pytest.fixture
def test_data():
    return {
        "Items": [
            {
                "pk": "CPT CODE:99202",
                "sk": "CONCEPT:1013631",
                "typical_patient": ("Office visit for a new patient with a small subdermal mass "
                                    "that does not require treatment."
                ),
                "pre_service_info": "nan",
                "intra_service_info": (
                    "Within 3 Days Prior to Visit: Review prior medical records and data. "
                    "Incorporate pertinent information into the medical record. "
                    "Communicate with other members of the health care team "
                    "regarding the visit. "
                    "Day of Visit: Confirm patient's identity. "
                    "Review the medical history forms completed by the patient. "
                    "Review vital signs obtained by clinical staff. "
                    "Obtain a medically appropriate history, "
                    "including pertinent components of history of present illness (HPI), "
                    "review of systems, social history, family history, and allergies, "
                    "and reconcile the patient's medications. "
                    "Perform a medically appropriate examination. "
                    "Synthesize the relevant history and physical examination to formulate"
                    "a differential diagnosis and treatment plan "
                    "(requiring straightforward medical decision making [MDM]). "
                    "Discuss treatment plan with the patient and family. "
                    "Provide patient education and respond to questions from "
                    "the patient and/or family. Document the encounter in the medical record. "
                    "Perform electronic data capture and reporting to comply with the quality "
                    "payment program and other electronic mandates. "
                    "Within 7 Days After Visit: Answer follow-up questions from the patient "
                    "and/or family that may occur within 7 days after the visit "
                    "and respond to treatment failures."
                ),
                "post_service_info": "nan",
                "ruc_reviewed_date": "2019-04"
            }
        ]
    }

@pytest.fixture
def mappings():
    return [
        {
            "pk": {"S": "CPT CODE:123"},
            "typical_patient": {"S": "Patient Info"},
            "pre_service_info": {"S": "Pre-Service Info"},
            "intra_service_info": {"S": "Intra-Service Info"},
            "post_service_info": {"S": "Post-Service Info"},
            "ruc_reviewed_date": {"S": "Reviewed Date"},
            "sk": {"S": "CONCEPT:456"},
        }
    ]
