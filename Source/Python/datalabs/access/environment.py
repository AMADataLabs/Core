"""Class for loading environment"""
import logging
import os

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class VariableTree:
    def __init__(self, root, separator=None):
        self._root = root
        self._separator = separator or '_'

    def __repr__(self):
        return str(self._root)

    @classmethod
    def generate(cls, separator=None):
        ''' Generate a VariableTree from all current environment variables. '''
        root = dict()

        # pylint: disable=protected-access
        for name, value in os.environ._data.items():
            cls._create_branch(root, name.decode('utf-8'), value.decode('utf-8'))

        return VariableTree(root, separator)

    def get_value(self, branches: list):
        branch = self._root

        for next_branch in branches:
            value = branch[next_branch]['value']
            branch = branch[next_branch]['branches']

        return value

    def get_branches(self, branches: list):
        branch = self._root

        for next_branch in branches:
            branch = branch[next_branch]['branches']

        return list(branch.keys())

    def get_branch_values(self, branches: list):
        branch = self._root

        for next_branch in branches:
            branch = branch[next_branch]['branches']

        return {key:branch[key]['value'] for key in branch.keys()}


    @classmethod
    def _create_branch(cls, trunk, name, value):
        LOGGER.debug('Name: %s', name)
        if self._separator in name:
            prefix, suffix = name.split(self._separator', 1)
            LOGGER.debug('Prefix: %s\tSuffix: %s', prefix, suffix)

            if prefix not in trunk:
                trunk[prefix] = dict(
                    branches=dict(),
                    value=None,
                )

            if prefix and suffix:
                cls._create_branch(trunk[prefix]['branches'], suffix, value)
        else:
            if name not in trunk:
                trunk[name] = dict(
                    branches=dict(),
                    value=None,
                )

            trunk[name]['value'] = value
