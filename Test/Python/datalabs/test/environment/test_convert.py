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


def test_dependency_lines_are_parsed_correctly(pipfile_template_filename):
    converter = Conda2PipenvEnvrionmentConverter(None, None)

    variable, value = converter._parse_conda_dependency('conda=4.8.2=py37_0')

    assert variable == 'conda'
    assert value == '4.8.2'


def test_read_template_succeeds(pipfile_template_filename):
    converter = Conda2PipenvEnvrionmentConverter(None, None)

    template = converter._read_template(pipfile_template_filename)


def test_dependency_lines_are_parsed_correctly(pipfile_template_filename):
    converter = Conda2PipenvEnvrionmentConverter(None, None)

    variable, value = converter._parse_conda_dependency('conda=4.8.2=py37_0')

    assert variable == 'conda'
    assert value == '4.8.2'


def test_pipfile_template_renders_correctly(pipfile_template_filename, expected_conda_packages, expected_rendered_template):
    converter = Conda2PipenvEnvrionmentConverter(None, None)
    template = converter._read_template(pipfile_template_filename)

    rendered_template = converter._render_template(template, expected_conda_packages)

    assert expected_rendered_template == rendered_template


def test_conda_environment_correctly_converted_to_pipenv(conda_package_list_filename, pipfile_template_filename, expected_rendered_template):
    converter = Conda2PipenvEnvrionmentConverter(conda_package_list_filename, pipfile_template_filename)

    rendered_template = converter.convert()

    assert expected_rendered_template == rendered_template


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


@pytest.fixture
def expected_rendered_template():
    return '[[source]]\nname = "pypi"\nurl = "https://pypi.org/simple"\nverify_ssl = true\n\n[dev-packages]\n\n[packages]\n\nnumpy = \'==1.18.1\'\n\npandas = \'==1.0.0\'\n\nscipy = \'==1.3.2\'\n\n\n[requires]\npython_version = "3.7.6"'
