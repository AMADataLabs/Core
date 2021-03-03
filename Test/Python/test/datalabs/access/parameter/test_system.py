""" source: datalabs.access.environment.system """
import os

import pytest

from   datalabs.access.parameter.system import ReferenceEnvironmentLoader


# pylint: disable=redefined-outer-name, protected-access, unused-argument
def test_get_referent_variables_returns_only_referenceless_variables(environment):
    referent_variables = ReferenceEnvironmentLoader._get_referent_variables()

    assert len(referent_variables) == 3
    assert 'PYTEST_CURRENT_TEST' in referent_variables
    assert 'REFERENT_VARIABLE' in referent_variables
    assert 'PHRASE_VARIABLE' in referent_variables


# pylint: disable=redefined-outer-name, protected-access
def test_get_reference_variables_returns_no_referenceless_variables(environment):
    reference_variables = ReferenceEnvironmentLoader._get_reference_variables(environment)

    assert len(reference_variables) == len(environment) - 3
    assert 'PYTEST_CURRENT_TEST' not in reference_variables
    assert 'REFERENT_VARIABLE' not in reference_variables
    assert 'PHRASE_VARIABLE' not in reference_variables


# pylint: disable=redefined-outer-name, protected-access
def test_resolve_references_in_value_matches_simple_reference(environment):
    loader = ReferenceEnvironmentLoader.from_environ()
    referent_variables = loader._get_referent_variables()
    resolved_value = loader._resolve_references_in_value(environment['SIMPLE_REFERENCE_VARIABLE'], referent_variables)

    assert resolved_value == referent_variables['REFERENT_VARIABLE']


# pylint: disable=redefined-outer-name, protected-access
def test_resolve_references_in_value_matches_complex_reference(environment):
    loader = ReferenceEnvironmentLoader.from_environ()
    referent_variables = loader._get_referent_variables()
    resolved_value = loader._resolve_references_in_value(environment['COMPLEX_REFERENCE_VARIABLE'], referent_variables)

    assert resolved_value == 'I said, "Woopideedoo!"'


# pylint: disable=redefined-outer-name, protected-access
def test_resolve_references_in_value_matches_multiple_references(environment):
    loader = ReferenceEnvironmentLoader.from_environ()
    referent_variables = loader._get_referent_variables()
    resolved_value = loader._resolve_references_in_value(environment['MULTI_REFERENCE_VARIABLE'], referent_variables)

    assert resolved_value == 'He said, "Woopideedoo, I love you!"'


# pylint: disable=redefined-outer-name, unused-argument
def test_load_resolves_all_references(environment):
    loader = ReferenceEnvironmentLoader.from_environ()
    loader.load()

    assert len(os.environ) == 6
    assert os.environ.get('SIMPLE_REFERENCE_VARIABLE') == 'Woopideedoo'
    assert os.environ.get('COMPLEX_REFERENCE_VARIABLE') == 'I said, "Woopideedoo!"'
    assert os.environ.get('MULTI_REFERENCE_VARIABLE') == 'He said, "Woopideedoo, I love you!"'


@pytest.fixture
def environment():
    current_environment = os.environ.copy()
    os.environ.clear()

    os.environ['REFERENT_VARIABLE'] = 'Woopideedoo'
    os.environ['SIMPLE_REFERENCE_VARIABLE'] = '${REFERENT_VARIABLE}'
    os.environ['COMPLEX_REFERENCE_VARIABLE'] = 'I said, "${REFERENT_VARIABLE}!"'
    os.environ['PHRASE_VARIABLE'] = 'I love you!'
    os.environ['MULTI_REFERENCE_VARIABLE'] = 'He said, "${REFERENT_VARIABLE}, ${PHRASE_VARIABLE}"'

    yield os.environ

    os.environ.clear()
    os.environ.update(current_environment)
