""" Source: datalabs.deploy.etcd.load """
import tempfile

import pytest

from   datalabs.deploy.etcd.load import ConfigMapLoader


def test_configmap_variable_extraction(etcd_config, configmap):
    loader = ConfigMapLoader(etcd_config)

    variables = loader._extract_variables_from_configmap(configmap)

    assert len(variables) == 2
    assert 'JAZZ_SONG' in variables
    assert variables['JAZZ_SONG'] == 'My Funny Valentine'
    assert 'BLUES_SONG' in variables
    assert variables['BLUES_SONG'] == 'Born Under a Bad Sign'


def test_transaction_body_generation(etcd_config, configmap):
    loader = ConfigMapLoader(etcd_config)
    variables = loader._extract_variables_from_configmap(configmap)

    transaction = loader._generate_transaction_body(variables)

    assert len(transaction) == 1
    assert 'success' in transaction

    operations = transaction['success']
    assert len(operations) == 2
    for operation in operations:
        assert 'requestPut' in operation
        assert variables[operation['requestPut']['key']] == operation['requestPut']['value']


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
