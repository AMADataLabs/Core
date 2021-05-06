""" Source: datalabs.deploy.etcd.load """
import base64
import tempfile

import pytest

from   datalabs.deploy.etcd.load import ConfigMapLoader


# pylint: disable=redefined-outer-name, protected-access
def test_configmap_variable_extraction(etcd_config, configmap):
    loader = ConfigMapLoader(etcd_config)

    variables = loader._extract_variables_from_configmap(configmap)

    assert len(variables) == 2
    assert variables[0][0] == 'JAZZ_SONG'
    assert variables[0][1] == 'My Funny Valentine'
    assert variables[1][0] == 'BLUES_SONG'
    assert variables[1][1] == 'Born Under a Bad Sign'


# pylint: disable=redefined-outer-name, protected-access
def test_transaction_body_generation(etcd_config, configmap):
    loader = ConfigMapLoader(etcd_config)
    variables = loader._extract_variables_from_configmap(configmap)
    variable_map = dict(variables)

    transaction = loader._generate_transaction_body(variables)

    assert len(transaction) == 1
    assert 'success' in transaction

    operations = transaction['success']
    assert len(operations) == 2
    for operation in operations:
        key = base64.b64decode(operation['requestPut']['key'].encode('utf8')).decode('utf8')
        expected_value = base64.b64encode(variable_map[key].encode('utf8')).decode('utf8')
        assert expected_value == operation['requestPut']['value']


@pytest.fixture
def etcd_config():
    return dict(
        host='etcd-bogus.ama-assn.org',
        username='mjordan',
        password='bballgod123'
    )


@pytest.fixture
def filename():
    with tempfile.NamedTemporaryFile(suffix='.db', delete=True) as file:
        yield file.name


@pytest.fixture
# pylint: disable=redefined-outer-name
def configmap(filename):
    with open(filename, 'w') as file:
        file.write(
'''---
apiVersion: v1
kind: ConfigMap
metadata:
    name: bogus
    namespace: hsg-data-labs-dev
data:
    JAZZ_SONG: 'My Funny Valentine'
    BLUES_SONG: 'Born Under a Bad Sign'
'''
        )

    return filename
