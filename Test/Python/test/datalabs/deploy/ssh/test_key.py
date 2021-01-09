""" source: datalabs.deploy.ssh.key """
from   collections import namedtuple
import os
import stat
import tempfile

import pytest

from   datalabs.deploy.ssh.key import load_key_from_variable


# pylint: disable=redefined-outer-name
def test_load_key_from_variable_has_correct_content(variable, path):
    load_key_from_variable(variable.name, path)

    with open(path) as file:
        key = file.read()

    assert key == variable.value


# pylint: disable=redefined-outer-name
def test_load_key_from_variable_has_correct_permissions(variable, path):
    load_key_from_variable(variable.name, path)

    mode = stat.S_IMODE(os.stat(path).st_mode)

    assert mode == 0o400


@pytest.fixture
def variable():
    Variable = namedtuple('Variable', 'name, value')
    name = 'TEST_SSH_KEY'
    # The following is a valid, but unused, private key. It's probably overkill,
    # but, you know, whatever man.
    value = '''-----BEGIN OPENSSH PRIVATE KEY-----
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
68BpMJ6vcfA1T3hbDNYGRKDb5lQ=
-----END OPENSSH PRIVATE KEY-----'''
    current_environment = os.environ.copy()

    os.environ[name] = value

    yield Variable(name, value)

    os.environ.clear()
    os.environ.update(current_environment)


@pytest.fixture
def path():
    with tempfile.TemporaryDirectory() as temp_directory:
        yield os.path.join(temp_directory, 'id_rsa')
