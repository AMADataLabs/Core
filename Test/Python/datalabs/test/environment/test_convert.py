import logging
import pytest

from   datalabs.environment.convert import Conda2PipenvEnvrionmentConverter

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def test_dependency_dict_matches_conda_package_list(conda_package_list_filename, expected_conda_packages):
    converter = Conda2PipenvEnvrionmentConverter(None, None)

    dependencies = converter._read_conda_dependencies(conda_package_list_filename)

    assert expected_conda_packages == dependencies


@pytest.fixture
def conda_package_list_filename():
    return 'Test/Python/datalabs/test/environment/conda_package_list.txt'


@pytest.fixture
def pipfile_template_filename():
    return 'Test/Python/datalabs/test/environment/Pipfile_template.txt'


@pytest.fixture
def expected_conda_packages():
    return dict(
        conda='4.8.2',
        numpy='1.18.1',
        pandas='1.0.0',
        python='3.7.6',
        scipy='1.3.2',
    )
