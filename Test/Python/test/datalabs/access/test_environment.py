""" source: datalabs.access.environment """
import os
import pytest

from   datalabs.access.environment import VariableTree


# pylint: disable=redefined-outer-name
def test_get_branches(tree):
    assert tree.get_value(['ONE', 'TWO', 'BUCKLE']) == 'foo'
    assert tree.get_value(['ONE', 'TWO', 'MY']) == 'bar'
    assert tree.get_value(['ONE', 'TWO', 'SHOE']) == 'party'

    branches = ['BUCKLE', 'MY', 'SHOE']

    for branch in branches:
        assert branch in branches


# pylint: disable=redefined-outer-name
def test_get_branch(tree):
    branches = tree.get_branches(['ONE', 'TWO'])

    for branch in ['BUCKLE', 'MY', 'SHOE']:
        assert branch in branches


# pylint: disable=redefined-outer-name
def test_get_branch_values(tree):
    values = tree.get_branch_values(['ONE', 'TWO'])

    for key, value in zip(['BUCKLE', 'MY', 'SHOE'], ['foo', 'bar', 'party']):
        assert values[key] == value


@pytest.fixture
def tree():
    os.environ['ONE_TWO_BUCKLE'] = 'foo'
    os.environ['ONE_TWO_MY'] = 'bar'
    os.environ['ONE_TWO_SHOE'] = 'party'

    return VariableTree.generate()
