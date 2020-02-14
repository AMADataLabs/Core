import logging
import os
import pytest
import tempfile

import datalabs.environment.setup as setup

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def test_dependency_dict_matches_package_list(pipenv_filenames, python_version, expected_packages):
    generator = setup.PipenvEnvironmentGenerator(pipenv_filenames, python_version=python_version)

    dependencies = generator._read_dependencies()

    assert expected_packages == dependencies


def test_dependency_dict_matches_whitelist(whitelisting_pipenv_filenames, python_version, expected_packages, expected_whitelist):
    generator = setup.PipenvEnvironmentGenerator(whitelisting_pipenv_filenames, python_version=python_version)
    whitelisted_packages = {k:v for k,v in expected_packages.items() if k in expected_whitelist}

    dependencies = generator._read_dependencies()

    assert whitelisted_packages == dependencies


def test_dependency_lines_are_parsed_correctly(pipenv_filenames, python_version):
    generator = setup.PipenvEnvironmentGenerator(pipenv_filenames, python_version=python_version)

    variable, value = generator._parse_dependency('conda==4.8.2')

    assert variable == 'conda'
    assert value == '4.8.2'


def test_read_whitelist_returns_correct_package_list(whitelisting_pipenv_filenames, python_version):
    generator = setup.PipenvEnvironmentGenerator(whitelisting_pipenv_filenames, python_version=python_version)

    whitelist = generator._read_whitelist()

    assert len(whitelist) == 2
    assert 'numpy' in whitelist
    assert 'scipy' in whitelist


def test_read_template_succeeds(pipenv_filenames, python_version):
    generator = setup.PipenvEnvironmentGenerator(pipenv_filenames, python_version=python_version)

    template = generator._read_template()


def test_pipfile_template_renders_correctly(pipenv_filenames, python_version, expected_packages, expected_rendered_pipfile_template):
    generator = setup.PipenvEnvironmentGenerator(pipenv_filenames, python_version=python_version)
    template = generator._read_template()
    package_versions = [(name,value) for name,value in sorted(expected_packages.items())]
    template_parameters = dict(package_versions=package_versions, python_version=python_version)
    LOGGER.debug(f'Template Parameters: {template_parameters}')

    rendered_template = generator._render_template(template, template_parameters)
    LOGGER.debug(f'Expected Pipfile: {expected_rendered_pipfile_template}')
    LOGGER.debug(f'Actual Pipfile: {rendered_template}')

    assert expected_rendered_pipfile_template == rendered_template


def test_environment_correctly_converted_to_pipenv(pipenv_filenames, python_version, expected_rendered_pipfile_template):
    generator = setup.PipenvEnvironmentGenerator(pipenv_filenames, python_version=python_version)

    generator.generate()

    rendered_template = None
    with open(pipenv_filenames.output) as file:
        rendered_template = file.read()
    LOGGER.debug(f'Rendered Pipfile: {rendered_template}')

    assert expected_rendered_pipfile_template == rendered_template


def test_environment_correctly_converted_to_pip(pip_filenames, python_version, expected_rendered_requirements_template):
    generator = setup.PipEnvironmentGenerator(pip_filenames)

    generator.generate()

    rendered_template = None
    with open(pip_filenames.output) as file:
        rendered_template = file.read()
    LOGGER.debug(f'Rendered Requirements: {rendered_template}')

    assert expected_rendered_requirements_template == rendered_template


def test_environment_correctly_converted_to_conda(conda_filenames, python_version, expected_rendered_conda_requirements_template):
    generator = setup.CondaEnvironmentGenerator(conda_filenames, python_version=python_version)

    generator.generate()

    rendered_template = None
    with open(conda_filenames.output) as file:
        rendered_template = file.read()
    LOGGER.debug(f'Rendered Conda Requirements: {rendered_template}')

    assert expected_rendered_conda_requirements_template == rendered_template


@pytest.fixture
def pipenv_filenames():
    output_file = tempfile.NamedTemporaryFile()
    output_file.close()

    return setup.EnvironmentFilenames(
        package_list='Test/Python/datalabs/test/environment/requirements.txt',
        template='Test/Python/datalabs/test/environment/Pipfile_template.txt',
        output=output_file.name,
        whitelist=None
    )


@pytest.fixture
def whitelisting_pipenv_filenames(pipenv_filenames):
    return setup.EnvironmentFilenames(
        package_list=pipenv_filenames.package_list,
        template=pipenv_filenames.template,
        output=pipenv_filenames.output,
        whitelist = 'Test/Python/datalabs/test/environment/package_selection.csv',
    )


@pytest.fixture
def pip_filenames():
    output_file = tempfile.NamedTemporaryFile()
    output_file.close()

    return setup.EnvironmentFilenames(
        package_list='Test/Python/datalabs/test/environment/requirements.txt',
        template='Test/Python/datalabs/test/environment/requirements_template.txt',
        output=output_file.name,
        whitelist=None
    )


@pytest.fixture
def conda_filenames():
    output_file = tempfile.NamedTemporaryFile()
    output_file.close()

    return setup.EnvironmentFilenames(
        package_list='Test/Python/datalabs/test/environment/requirements.txt',
        template='Test/Python/datalabs/test/environment/conda_requirements_template.txt',
        output=output_file.name,
        whitelist=None
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


@pytest.fixture
def expected_rendered_requirements_template():
    return '\nnumpy==1.18.1\npandas==1.0.0\nscipy==1.3.2'


@pytest.fixture
def expected_rendered_conda_requirements_template():
    return '\nnumpy=1.18.1\npandas=1.0.0\npython=3.7\nscipy=1.3.2'
