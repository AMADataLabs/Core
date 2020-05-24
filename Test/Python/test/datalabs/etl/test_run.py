import os

import pytest

import datalabs.etl.run as run


def test_etl_configurations_are_collected_and_trimed_as_expected(function_names, environment):
    for name in function_names:
        _test_etl_configuration_is_collected_and_trimed_as_expected(name, environment)


# pylint: disable=protected-access
def _test_etl_configuration_is_collected_and_trimed_as_expected(name, environment):
        configuration = run._generate_app_configuration(name)

        assert len(configuration) == 8

        for key in ['LAMBDA_FUNCTION', 'APP', 'EXTRACTOR', 'EXTRACTOR_FOO', 'LOADER', 'LOADER_FOO', 'TRANSFORMER', 'TRANSFORMER_FOO']:
            assert key in configuration


        for key, method in {'EXTRACTOR':'extract', 'LOADER':'load', 'TRANSFORMER':'transform'}.items():
            assert hasattr(configuration[key], method)

            assert configuration[key]._configuration['FOO'] == 'bar'


@pytest.fixture
def function_names():
    return ['TestFunction1', 'TestFunction2']


@pytest.fixture
def environment(function_names):
    configuration = dict(
        ETL_TESTFUNCTION1_LAMBDA_FUNCTION=function_names[0],
        ETL_TESTFUNCTION1_APP='test.datalabs.etl.app.ETL1',
        ETL_TESTFUNCTION1_EXTRACTOR='test.datalabs.etl.extract.TestExtractor',
        ETL_TESTFUNCTION1_EXTRACTOR_FOO='bar',
        ETL_TESTFUNCTION1_TRANSFORMER='test.datalabs.etl.transform.TestTransformer',
        ETL_TESTFUNCTION1_TRANSFORMER_FOO='bar',
        ETL_TESTFUNCTION1_LOADER='test.datalabs.etl.load.TestLoader',
        ETL_TESTFUNCTION1_LOADER_FOO='bar',
        ETL_TESTFUNCTION2_LAMBDA_FUNCTION=function_names[1],
        ETL_TESTFUNCTION2_APP='test.datalabs.etl.app.ETL2',
        ETL_TESTFUNCTION2_EXTRACTOR='test.datalabs.etl.extract.TestExtractor',
        ETL_TESTFUNCTION2_EXTRACTOR_FOO='bar',
        ETL_TESTFUNCTION2_TRANSFORMER='test.datalabs.etl.transform.TestTransformer',
        ETL_TESTFUNCTION2_TRANSFORMER_FOO='bar',
        ETL_TESTFUNCTION2_LOADER='test.datalabs.etl.load.TestLoader',
        ETL_TESTFUNCTION2_LOADER_FOO='bar',
    )

    for name, value in configuration.items():
        os.environ[name] = value

    yield configuration

    for name, value in configuration.items():
        os.environ.pop(name)
