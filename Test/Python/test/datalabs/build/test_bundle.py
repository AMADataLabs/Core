""" source: datalabs.build.bundle """
import logging
import os
import tempfile

import pytest

import datalabs.build.bundle as bundle

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=redefined-outer-name, protected-access
def test_load_module_spec(modspec_file):
    modspec_yaml = bundle.SourceBundle._load_module_spec(modspec_file)

    LOGGER.debug(modspec_yaml)
    assert modspec_yaml.startswith('\n---\nmodspec:\n')


# pylint: disable=redefined-outer-name, protected-access
def test_parse_module_spec(modspec_file):
    modspec_yaml = bundle.SourceBundle._load_module_spec(modspec_file)
    modspec = bundle.SourceBundle._parse_module_spec(modspec_yaml)

    LOGGER.debug(modspec)
    assert 'modspec' in modspec


# pylint: disable=redefined-outer-name
def test_files(modspec_file, base_path):
    source_files = bundle.SourceBundle(modspec_file).files(base_path)

    LOGGER.debug(source_files)
    assert len(source_files) == 8


# pylint: disable=redefined-outer-name
def test_copy(modspec_file, base_path, app_path):
    bundle.SourceBundle(modspec_file).copy(base_path, app_path)
    file_count = 0

    for _, _, files in os.walk(app_path):
        file_count += len(files)

    assert file_count == 8


@pytest.fixture
def modspec_file():
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
