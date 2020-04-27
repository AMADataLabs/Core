import os

import pytest
# import datalabs.etl.cpt.trigger as trigger


def test_etl_configuration_is_collected_and_trimed_as_expected(function_names, environment):
    pass
    # for name in function_names:
    #     trigger._generate_app_configuration(name)


@pytest.fixture
def function_names():
    return ['TestFunction1', 'TestFunction2']


@pytest.fixture
def environment(function_names):
    configuration = dict(
        ETL_CSV_LAMBDA_FUNCTION=function_names[0],
        ETL_CSV_EXTRACTOR='test.datalabs.etl.extract.TestExtractor',
        ETL_CSV_EXTRACTOR_FOO='bar',
        ETL_CSV_LOADER='test.datalabs.etl.load.TestLoader',
        ETL_CSV_LOADER_PING='pong',
        ETL_DATABASE_LAMBDA_FUNCTION=function_names[1],
        ETL_DATABASE_EXTRACTOR='test.datalabs.etl.extract.TestExtractor',
        ETL_DATABASE_EXTRACTOR_BIFF='baff',
        ETL_DATABASE_LOADER='test.datalabs.etl.load.TestLoader',
        ETL_DATABASE_LOADER_BOINK='bonk',
    )

    for name, value in configuration.items():
        os.environ[name] = value

    yield configuration

    for name, value in configuration.items():
        os.environ.pop(name)
