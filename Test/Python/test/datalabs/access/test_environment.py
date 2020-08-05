""" source: datalabs.access.environment """
import os
import pytest

from   datalabs.access.environment import VariableTree


# pylint: disable=redefined-outer-name
def test_get_branches(tree):
    assert 'foo' == tree.get_value(['ONE', 'TWO', 'BUCKLE'])
    assert 'bar' == tree.get_value(['ONE', 'TWO', 'MY'])
    assert 'party' == tree.get_value(['ONE', 'TWO', 'SHOE'])

    for branch in ['BUCKLE', 'MY', 'SHOE']:
        assert branch in branches


# pylint: disable=redefined-outer-name
def test_get_branches(tree):
    branches = tree.get_branches(['ONE', 'TWO'])

    for branch in ['BUCKLE', 'MY', 'SHOE']:
        assert branch in branches


# pylint: disable=redefined-outer-name
def test_get_branch_values(tree):
    values = tree.get_branch_values(['ONE', 'TWO'])

    for value in ['foo', 'bar', 'party']:
        assert value in values


@pytest.fixture
def tree():
    os.environ['ONE_TWO_BUCKLE'] = 'foo'
    os.environ['ONE_TWO_MY'] = 'bar'
    os.environ['ONE_TWO_SHOE'] = 'party'

    return VariableTree.generate()
