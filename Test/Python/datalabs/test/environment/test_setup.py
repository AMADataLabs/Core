import logging
import os
import pytest
import tempfile

from   datalabs.environment.setup import PipenvEnvironmentGenerator, GeneratorFilenames

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def test_dependency_dict_matches_package_list(filenames, python_version, expected_packages):
    generator = PipenvEnvironmentGenerator(filenames, python_version)

    dependencies = generator._read_dependencies()

    assert expected_packages == dependencies


def test_dependency_dict_matches_whitelist(whitelisting_filenames, python_version, expected_packages, expected_whitelist):
    generator = PipenvEnvironmentGenerator(whitelisting_filenames, python_version)
    whitelisted_packages = {k:v for k,v in expected_packages.items() if k in expected_whitelist}

    dependencies = generator._read_dependencies()

    assert whitelisted_packages == dependencies


def test_dependency_lines_are_parsed_correctly(filenames, python_version):
    generator = PipenvEnvironmentGenerator(filenames, python_version)

    variable, value = generator._parse_dependency('conda==4.8.2')

    assert variable == 'conda'
    assert value == '4.8.2'


def test_read_whitelist_returns_correct_package_list(whitelisting_filenames, python_version):
    generator = PipenvEnvironmentGenerator(whitelisting_filenames, python_version)

    whitelist = generator._read_whitelist()

    assert len(whitelist) == 2
    assert 'numpy' in whitelist
    assert 'scipy' in whitelist


def test_read_template_succeeds(filenames, python_version):
    generator = PipenvEnvironmentGenerator(filenames, python_version)

    template = generator._read_template()


def test_pipfile_template_renders_correctly(filenames, python_version, expected_packages, expected_rendered_pipfile_template):
    generator = PipenvEnvironmentGenerator(filenames, python_version)
    template = generator._read_template()

    rendered_template = generator._render_template(template, expected_packages)

    assert expected_rendered_pipfile_template == rendered_template


def test_environment_correctly_converted_to_pipenv(filenames, python_version, expected_rendered_pipfile_template):
    generator = PipenvEnvironmentGenerator(filenames, python_version)

    generator.generate()

    rendered_template = None
    with open(filenames.configuration) as file:
        rendered_template = file.read()
    logger.debug(f'Rendered Template: {rendered_template}')

    assert expected_rendered_pipfile_template == rendered_template


@pytest.fixture
def filenames():
    configuration_file = tempfile.NamedTemporaryFile()
    configuration_file.close()

    yield GeneratorFilenames(
        package_list='Test/Python/datalabs/test/environment/requirements.txt',
        template='Test/Python/datalabs/test/environment/Pipfile_template.txt',
        configuration=configuration_file.name,
        whitelist=None
    )


@pytest.fixture
def whitelisting_filenames(filenames):
    yield GeneratorFilenames(
        package_list=filenames.package_list,
        template=filenames.template,
        configuration=filenames.configuration,
        whitelist = 'Test/Python/datalabs/test/environment/package_selection.csv',
    )


@pytest.fixture
def python_version():
    return '3.7'


@pytest.fixture
def expected_whitelist():
    return ['numpy', 'scipy']


@pytest.fixture
def expected_packages():
    return dict(
        numpy='1.18.1',
        pandas='1.0.0',
        scipy='1.3.2',
    )


@pytest.fixture
def expected_rendered_pipfile_template():
    return '[[source]]\nname = "pypi"\nurl = "https://pypi.org/simple"\nverify_ssl = true\n\n[dev-packages]\n\n[packages]\n\nnumpy = \'==1.18.1\'\npandas = \'==1.0.0\'\nscipy = \'==1.3.2\'\n\n[requires]\npython_version = "3.7"'
