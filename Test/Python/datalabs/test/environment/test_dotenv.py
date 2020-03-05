import logging
import os
import pytest
import dotenv

import datalabs.environment.setup as setup

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def test_dotenv_finds_configuration_file():
    dotenv.load_dotenv(dotenv.find_dotenv())

    test_variable = os.environ.get('DATALABS_TEST_VARIABLE_OMICRON_OMEGA')

    assert test_variable == 'Howdy, Partner!'
