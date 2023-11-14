""" source: datalabs.etl.marketing.aggregate.transform """
import mock
import pytest

from   datalabs.etl.marketing.aggregate.poll import AtDataStatusPollingTask


# pylint: disable=redefined-outer-name, protected-access
def test_poll_for_validation_status(transformer, request_parameters_data, get_response):
    with mock.patch(
        "datalabs.etl.marketing.aggregate.poll.AtDataStatusPollingTask._is_ready",
        return_value=get_response
    ) as mock_json_load:

        mock_json_load.return_value=get_response.data
        is_ready = transformer._is_ready(request_parameters_data)

        assert is_ready is False


@pytest.fixture
def parameters():
    return dict(
        HOST='portal.freshaddress.com',
        ACCOUNT='AB254_16345',
        API_KEY='D02502F2-382A-4F8D-983E-3B3B82ABFD5B'
    )


# pylint: disable=redefined-outer-name
@pytest.fixture
def transformer(parameters):
    return AtDataStatusPollingTask(parameters)


@pytest.fixture
def get_response():
    mock_response = mock.Mock()
    #mock_response.data = {"request_id": "a319725", "results_filename": "emails_20231102-152626_Results_12.txt"}
    mock_response.data = False

    return mock_response


@pytest.fixture
def request_parameters_data():
    return b"""{"request_id": "a319725", "results_filename": null}"""
