import logging
import os
import pytest
import tempfile

from   datalabs.environment.convert import Conda2PipenvEnvrionmentConverter, ConversionFilenames

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def test_dependency_dict_matches_conda_package_list(filenames, expected_conda_packages):
    converter = Conda2PipenvEnvrionmentConverter(filenames)

    dependencies = converter._read_conda_dependencies()

    assert expected_conda_packages == dependencies


def test_dependency_dict_matches_whitelist(whitelisting_filenames, expected_conda_packages, expected_whitelist):
    converter = Conda2PipenvEnvrionmentConverter(whitelisting_filenames)
    whitelisted_conda_packages = {k:v for k,v in expected_conda_packages.items() if k in expected_whitelist}

    dependencies = converter._read_conda_dependencies()

    assert whitelisted_conda_packages == dependencies


def test_dependency_lines_are_parsed_correctly(filenames):
    converter = Conda2PipenvEnvrionmentConverter(filenames)

    variable, value = converter._parse_conda_dependency('conda=4.8.2=py37_0')

    assert variable == 'conda'
    assert value == '4.8.2'


def test_read_whitelist_returns_correct_package_list(whitelisting_filenames):
    converter = Conda2PipenvEnvrionmentConverter(whitelisting_filenames)

    whitelist = converter._read_whitelist()

    assert len(whitelist) == 2
    assert 'numpy' in whitelist
    assert 'scipy' in whitelist


def test_read_template_succeeds(filenames):
    converter = Conda2PipenvEnvrionmentConverter(filenames)

    template = converter._read_template()


def test_dependency_lines_are_parsed_correctly(filenames):
    converter = Conda2PipenvEnvrionmentConverter(filenames)

    variable, value = converter._parse_conda_dependency('conda=4.8.2=py37_0')

    assert variable == 'conda'
    assert value == '4.8.2'


def test_pipfile_template_renders_correctly(filenames, expected_conda_packages, expected_rendered_template):
    converter = Conda2PipenvEnvrionmentConverter(filenames)
    template = converter._read_template()

    rendered_template = converter._render_template(template, expected_conda_packages)

    assert expected_rendered_template == rendered_template


def test_conda_environment_correctly_converted_to_pipenv(filenames, expected_rendered_template):
    converter = Conda2PipenvEnvrionmentConverter(filenames)

    converter.convert()

    rendered_template = None
    with open(filenames.converted_dependencies) as file:
        rendered_template = file.read()

    assert expected_rendered_template == rendered_template


@pytest.fixture
def filenames():
    converted_dependencies_file = tempfile.NamedTemporaryFile()
    converted_dependencies_file.close()

    yield ConversionFilenames(
        conda_package_list='Test/Python/datalabs/test/environment/conda_package_list.txt',
        template='Test/Python/datalabs/test/environment/Pipfile_template.txt',
        converted_dependencies=converted_dependencies_file.name,
        whitelist=None
    )


@pytest.fixture
def whitelisting_filenames(filenames):
    yield ConversionFilenames(
        conda_package_list=filenames.conda_package_list,
        template=filenames.template,
        converted_dependencies=filenames.converted_dependencies,
        whitelist = 'Test/Python/datalabs/test/environment/package_selection.csv',
    )


@pytest.fixture
def expected_whitelist():
    return ['numpy', 'scipy']


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
    return '[[source]]\nname = "pypi"\nurl = "https://pypi.org/simple"\nverify_ssl = true\n\n[dev-packages]\n\n[packages]\n\nnumpy = \'==1.18.1\'\npandas = \'==1.0.0\'\nscipy = \'==1.3.2\'\n\n[requires]\npython_version = "3.7.6"'
