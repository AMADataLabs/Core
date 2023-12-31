""" source: datalabs.environment.setup """
import logging
import tempfile

import pytest

from   datalabs.environment import setup

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=redefined-outer-name, protected-access
def test_dependency_dict_matches_package_list(pipenv_filenames, python_version, expected_packages):
    generator = setup.PipenvEnvironmentGenerator(pipenv_filenames, python_version=python_version)

    dependencies = generator._read_dependencies()

    assert expected_packages == dependencies


# pylint: disable=redefined-outer-name, protected-access
def test_dependency_dict_matches_whitelist(
        whitelisting_pipenv_filenames, python_version, expected_packages, expected_whitelist
):
    generator = setup.PipenvEnvironmentGenerator(whitelisting_pipenv_filenames, python_version=python_version)
    whitelisted_packages = {k:v for k, v in expected_packages.items() if k in expected_whitelist}

    dependencies = generator._read_dependencies()

    assert whitelisted_packages == dependencies


# pylint: disable=redefined-outer-name, protected-access
def test_dependency_lines_are_parsed_correctly(pipenv_filenames, python_version):
    generator = setup.PipenvEnvironmentGenerator(pipenv_filenames, python_version=python_version)

    variable, value = generator._parse_dependency('conda==4.8.2')

    assert variable == 'conda'
    assert value == '4.8.2'


# pylint: disable=redefined-outer-name, protected-access
def test_read_whitelist_returns_correct_package_list(whitelisting_pipenv_filenames, python_version):
    generator = setup.PipenvEnvironmentGenerator(whitelisting_pipenv_filenames, python_version=python_version)

    whitelist = generator._read_whitelist()

    assert len(whitelist) == 2
    assert 'numpy' in whitelist
    assert 'scipy' in whitelist


# pylint: disable=redefined-outer-name, protected-access
def test_read_template_succeeds(pipenv_filenames, python_version):
    generator = setup.PipenvEnvironmentGenerator(pipenv_filenames, python_version=python_version)

    generator._read_template()


# pylint: disable=redefined-outer-name, protected-access
def test_pipfile_template_renders_correctly(
        pipenv_filenames, python_version, expected_packages, expected_rendered_pipfile_template
):
    generator = setup.PipenvEnvironmentGenerator(pipenv_filenames, python_version=python_version)
    template = generator._read_template()
    package_versions = sorted(expected_packages.items())
    template_parameters = dict(package_versions=package_versions, python_version=python_version)
    LOGGER.debug('Template Parameters: %s', template_parameters)

    rendered_template = generator._render_template(template, template_parameters)
    LOGGER.debug('Expected Pipfile: %s', expected_rendered_pipfile_template)
    LOGGER.debug('Actual Pipfile: %s', rendered_template)

    assert expected_rendered_pipfile_template == rendered_template


# pylint: disable=redefined-outer-name
def test_environment_correctly_converted_to_pipenv(
        pipenv_filenames, python_version, expected_rendered_pipfile_template
):
    generator = setup.PipenvEnvironmentGenerator(pipenv_filenames, python_version=python_version)

    generator.generate()

    rendered_template = None
    with open(pipenv_filenames.output, encoding="utf-8") as file:
        rendered_template = file.read()
    LOGGER.debug('Expected Pipfile: %s', expected_rendered_pipfile_template)
    LOGGER.debug('Rendered Pipfile: %s', rendered_template)

    assert expected_rendered_pipfile_template == rendered_template


# pylint: disable=redefined-outer-name
def test_environment_correctly_converted_to_pip(
        pip_filenames, expected_rendered_requirements_template
):
    generator = setup.PipEnvironmentGenerator(pip_filenames)

    generator.generate()

    rendered_template = None
    with open(pip_filenames.output, encoding="utf-8") as file:
        rendered_template = file.read()
    LOGGER.debug('Rendered Requirements: %s', rendered_template)

    assert expected_rendered_requirements_template == rendered_template


# pylint: disable=redefined-outer-name
def test_environment_correctly_converted_to_conda(
        conda_filenames, python_version, expected_rendered_conda_requirements_template
):
    generator = setup.CondaEnvironmentGenerator(conda_filenames, python_version=python_version)

    generator.generate()

    rendered_template = None
    with open(conda_filenames.output, encoding="utf-8") as file:
        rendered_template = file.read()
    LOGGER.debug('Expected Conda Requirements: %s', expected_rendered_conda_requirements_template)
    LOGGER.debug('Rendered Conda Requirements: %s', rendered_template)

    assert expected_rendered_conda_requirements_template == rendered_template


@pytest.fixture
def pipenv_filenames():
    with tempfile.NamedTemporaryFile() as output_file:
        yield setup.EnvironmentFilenames(
            package_list='Test/Python/test/datalabs/environment/requirements.txt',
            template='Test/Python/test/datalabs/environment/Pipfile_template.txt',
            output=output_file.name,
            whitelist=None
        )


@pytest.fixture
def whitelisting_pipenv_filenames(pipenv_filenames):
    return setup.EnvironmentFilenames(
        package_list=pipenv_filenames.package_list,
        template=pipenv_filenames.template,
        output=pipenv_filenames.output,
        whitelist='Test/Python/test/datalabs/environment/package_selection.csv',
    )


@pytest.fixture
def pip_filenames():
    with tempfile.NamedTemporaryFile() as output_file:
        yield setup.EnvironmentFilenames(
            package_list='Test/Python/test/datalabs/environment/requirements.txt',
            template='Test/Python/test/datalabs/environment/requirements_template.txt',
            output=output_file.name,
            whitelist=None
        )


@pytest.fixture
def conda_filenames():
    with tempfile.NamedTemporaryFile() as output_file:
        yield setup.EnvironmentFilenames(
            package_list='Test/Python/test/datalabs/environment/requirements.txt',
            template='Test/Python/test/datalabs/environment/conda_requirements_template.txt',
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
    return '[[source]]\nname = "pypi"\nurl = "https://pypi.org/simple"\nverify_ssl = true\n\n[dev-packages]\n\n'\
           '[packages]\nnumpy = \'==1.18.1\'\npandas = \'==1.0.0\'\nscipy = \'==1.3.2\'\n\n[requires]\n'\
           'python_version = "3.7"\n'


@pytest.fixture
def expected_rendered_requirements_template():
    return 'numpy==1.18.1\npandas==1.0.0\nscipy==1.3.2\n'


@pytest.fixture
def expected_rendered_conda_requirements_template():
    return 'numpy=1.18.1\npandas=1.0.0\npython=3.7\nscipy=1.3.2\n'
