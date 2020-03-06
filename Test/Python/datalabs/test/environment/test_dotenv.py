import dotenv
import logging
import os
import pathlib
import pytest
import tempfile

import datalabs.environment.setup as setup

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def test_dotenv_ignores_missing_configuration_file(temp_directory, environment):
    test_variable = os.environ.get('DATALABS_TEST_VARIABLE_OMICRON_OMEGA')
    assert test_variable is None

    # The argument to load_dotenv in conjunction with temp_directory
    # simulates passing no arguments in a clean directory.
    dotenv.load_dotenv(dotenv.find_dotenv(usecwd=True))

    test_variable = os.environ.get('DATALABS_TEST_VARIABLE_OMICRON_OMEGA')
    assert test_variable is None


def test_dotenv_finds_configuration_file(temp_directory, dotenv_file, environment):
    test_variable = os.environ.get('DATALABS_TEST_VARIABLE_OMICRON_OMEGA')
    assert test_variable is None

    # The argument to load_dotenv in conjunction with temp_directory and dotenv_file
    # simulates passing no arguments with a .env in the script directory.
    dotenv.load_dotenv(dotenv.find_dotenv(usecwd=True))

    test_variable = os.environ.get('DATALABS_TEST_VARIABLE_OMICRON_OMEGA')
    assert test_variable == 'Howdy, Partner!'


def test_dotenv_finds_configuration_file(temp_directory, dotenv_file, environment):
    # The argument to load_dotenv in conjunction with temp_directory and dotenv_file
    # simulates passing no arguments with a .env in the script directory.
    dotenv.load_dotenv(dotenv.find_dotenv(usecwd=True))

    test_variable = os.environ.get('DATALABS_TEST_VARIABLE_BOOLEAN_BOLERO')
    assert test_variable == True


@pytest.fixture
def temp_directory():
    current_directory = os.getcwd()

    with tempfile.TemporaryDirectory() as temp_directory:
        os.chdir(temp_directory)

        yield temp_directory

    os.chdir(current_directory)


@pytest.fixture
def environment():
    current_environment = os.environ.copy()

    yield current_environment

    os.environ = current_environment

@pytest.fixture
def dotenv_file(temp_directory):
    filename = pathlib.Path(temp_directory, '.env')

    with open(filename, 'w') as file:
        file.write(
            "DATALABS_TEST_VARIABLE_OMICRON_OMEGA='Howdy, Partner!'\n"
            "DATALABS_TEST_VARIABLE_BOOLEAN_BOLERO=True\n"
        )

    yield str(filename)
