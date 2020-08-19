""" source: datalabs.feature """
import os

import pytest

import datalabs.feature as feature


# pylint: disable=redefined-outer-name
def test_feature_disabled_by_default(feature_name):
    os.environ.pop('ENABLE_FEATURE_' + feature_name)

    assert not feature.enabled(feature_name)


# pylint: disable=redefined-outer-name
def test_feature_disabled_when_not_true(feature_name):
    assert not feature.enabled(feature_name)


# pylint: disable=redefined-outer-name
def test_feature_enabled_when_variable_set(feature_name):
    os.environ['ENABLE_FEATURE_' + feature_name] = 'TrUe'

    assert feature.enabled(feature_name)


@pytest.fixture
def feature_name():
    feature_name = 'BOGUS_FEATURE_NAME_314159265358979323846'
    current_environment = os.environ.copy()

    os.environ['ENABLE_FEATURE_' + feature_name] = 'False'

    yield feature_name

    os.environ.clear()
    os.environ.update(current_environment)
