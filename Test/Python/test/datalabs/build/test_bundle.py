""" source: datalabs.build.bundle """
import logging
import os
import tempfile

import pytest

from   datalabs.build.bundle.python import PythonSourceBundle

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=redefined-outer-name, protected-access
def test_load_python_modspec(python_modspec_path):
    bundle = PythonSourceBundle.from_file(python_modspec_path)

    LOGGER.debug(bundle._modspec_yaml)
    assert bundle._modspec_yaml.startswith('\n---\nmodspec:\n')


# pylint: disable=redefined-outer-name, protected-access
def test_parse_python_module_spec(python_modspec_path):
    bundle = PythonSourceBundle.from_file(python_modspec_path)
    modspec = PythonSourceBundle._parse_module_spec(bundle._modspec_yaml)

    LOGGER.debug(modspec)
    assert 'modspec' in modspec


# pylint: disable=redefined-outer-name
def test_generate_python_files_list(python_modspec_path, base_path):
    source_files = PythonSourceBundle.from_file(python_modspec_path).files(base_path)

    LOGGER.debug(source_files)
    assert len(source_files) == 11


# pylint: disable=redefined-outer-name
def test_copy_python_files(python_modspec_path, base_path, app_path):
    PythonSourceBundle.from_file(python_modspec_path).copy(base_path, app_path)
    file_count = 0

    for _, _, files in os.walk(app_path):
        file_count += len(files)

    assert file_count == 11


@pytest.fixture
def python_modspec_path():
    modspec = '''
---
modspec:
  - package: datalabs
  - package: datalabs.access
    exclude:
      - ods
      - edw
      - file
  - package: datalabs.analysis
    include:
      - exception
  - package: datalabs.access.cpt.api
'''
    with tempfile.NamedTemporaryFile() as temp_file:
        with open(temp_file.name, 'w') as modspec_out:
            modspec_out.write(modspec)

        yield temp_file.name


@pytest.fixture
def base_path():
    with tempfile.TemporaryDirectory() as temp_dir:
        populate_directory(
            os.path.join(temp_dir, 'datalabs'),
            ['__init__.py', 'plugin.py']
        )

        populate_directory(
            os.path.join(temp_dir, 'datalabs/access'),
            ['__init__.py', 'ods.py', 'aims.py', 'edw.py', 'database.py', 'file.py', 'odbc.py']
        )

        populate_directory(
            os.path.join(temp_dir, 'datalabs/analysis'),
            ['__init__.py', 'exception.py', 'wslive.py']
        )

        populate_directory(
            os.path.join(temp_dir, 'datalabs/access/cpt'),
            ['__init__.py']
        )

        populate_directory(
            os.path.join(temp_dir, 'datalabs/access/cpt/api'),
            ['__init__.py', 'default.py']
        )

        yield temp_dir


@pytest.fixture
def app_path():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


def populate_directory(directory, files):
    os.makedirs(directory)

    for file in files:
        open(os.path.join(directory, file), 'w').close()

def get_files_in_directory(path):
    _, _, all_files = next(os.walk(path))

    return all_files
