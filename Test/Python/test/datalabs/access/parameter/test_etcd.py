''' Source: datalabs.access.parameter.etcd '''
import json
import logging
import os

import mock
import pytest
import requests

from   datalabs.access.parameter.etcd import EtcdEnvironmentLoader

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=redefined-outer-name, protected-access
def test_parameter_extraction(loader_parameters, raw_parameters, expected_parameters):
    loader = EtcdEnvironmentLoader(loader_parameters)

    parameters = loader._extract_parameters(raw_parameters)
    LOGGER.debug('Parameters: %s', parameters)

    for key, value in parameters.items():
        assert isinstance(key, str)
        assert isinstance(value, str)
        assert expected_parameters[key] == value


# pylint: disable=redefined-outer-name, protected-access
def test_authentication(loader_parameters, etcd):
    loader = EtcdEnvironmentLoader(loader_parameters)

    token = loader._authenticate(etcd)

    assert token == 'abcd1234'


# pylint: disable=redefined-outer-name, protected-access
def test_get_parameters(loader_parameters, etcd):
    loader = EtcdEnvironmentLoader(loader_parameters)

    parameters = loader._get_parameters_from_etcd()

    for key, value in parameters.items():
        assert isinstance(key, str)
        assert isinstance(value, str)
        assert expected_parameters[key] == value


# pylint: disable=redefined-outer-name, protected-access
def test_set_environment_variables(expected_parameters, environment):
    EtcdEnvironmentLoader._set_environment_variables_from_parameters(expected_parameters)

    for key, value in expected_parameters.items():
        assert os.environ.get(key) == value


# pylint: disable=redefined-outer-name, protected-access
def test_load(loader_parameters, raw_parameters, expected_parameters, environment):
    with mock.patch('datalabs.access.parameter.etcd.requests') as req:
        response = requests.Response()
        response._content = json.dumps(raw_parameters).encode('utf8')
        req.Session.return_value.post.return_value = response

        loader = EtcdEnvironmentLoader(loader_parameters)

    loader.load()
    LOGGER.debug('Environment: %s', os.environ)

    for key, value in expected_parameters.items():
        assert os.environ.get(key) == value


@pytest.fixture
def loader_parameters():
    return dict(
        HOST='etcd-test.ama-assn.org',
        PREFIX='MY_DAG__MY_TASK__',
        USERNAME='pooter',
        PASSWORD='welovevampires'
    )

@pytest.fixture
def raw_parameters():
    return {
        "header": {
            "cluster_id": "14841639068965178418",
            "member_id": "10276657743932975437",
            "revision": "22",
            "raft_term": "8"
        },
        "kvs": [
            {
                "key": "TVlfREFHX19NWV9UQVNLX19BQ0NFU1NfS0VZ",
                "create_revision": "19",
                "mod_revision": "22",
                "version": "4",
                "value": "JHtBQ0NFU1NfS0VZfQ=="
            },
            {
                "key": "TVlfREFHX19NWV9UQVNLX19CQVNFX1BBVEg=",
                "create_revision": "15",
                "mod_revision": "15",
                "version": "1",
                "value": "QU1BL015UHJvamVjdA=="
            }
        ],
        "count": "2",
        "token": "abcd1234"
    }


@pytest.fixture
def expected_parameters():
    return {
        'MY_DAG__MY_TASK__ACCESS_KEY': '${ACCESS_KEY}',
        'MY_DAG__MY_TASK__BASE_PATH': 'AMA/MyProject'
    }


@pytest.fixture
def etcd(raw_parameters):
    with mock.patch('datalabs.access.parameter.etcd.requests') as req:
        response = requests.Response()
        response._content = json.dumps(raw_parameters).encode('utf8')

        req.Session.return_value.post.return_value = response

        yield req.Session()


@pytest.fixture
def environment():
    current_environment = os.environ.copy()

    yield os.environ

    os.environ.clear()
    os.environ.update(current_environment)
