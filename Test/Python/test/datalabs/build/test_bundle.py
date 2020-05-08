""" source: datalabs.build.bundle """
import logging
import os
import tempfile

import pytest

import datalabs.build.bundle as bundle

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def test_load_module_spec(modspec_file):
    modspec_yaml = bundle.SourceBundle._load_module_spec(modspec_file)

    LOGGER.debug(modspec_yaml)
    assert modspec_yaml.startswith('\n---\nmodspec:\n')


def test_parse_module_spec(modspec_file):
    modspec_yaml = bundle.SourceBundle._load_module_spec(modspec_file)
    modspec = bundle.SourceBundle._parse_module_spec(modspec_yaml)

    LOGGER.debug(modspec)
    assert 'modspec' in modspec


def test_files(modspec_file, base_path):
    source_files = bundle.SourceBundle(modspec_file).files(base_path)

    LOGGER.debug(source_files)
    assert source_files is not None


@pytest.fixture
def modspec_file():
    modspec = '''
---
modspec:
  - package: datalabs
  - package: datalabs.access
    exclude:
      - odb
      - aims
      - edw
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
            os.path.join(temp_dir.name, 'Source/Python/datalabs'),
            ['__init__.py', 'plugin.py']
        )

        populate_directory(
            os.path.join(temp_dir.name, 'Source/Python/datalabs/access'),
            ['__init__.py', 'odb.py', 'aims.py', 'edw.py', 'database.py', 'file.py']
        )

        populate_directory(
            os.path.join(temp_dir.name, 'Source/Python/datalabs/analysis'),
            ['__init__.py', 'exception.py', 'wslive.py']
        )

        yield temp_dir.name

def populate_directory(directory, files):
    os.mkdir(directory)

    for file in files:
        open(os.path.join(directory, file), 'w').close()
