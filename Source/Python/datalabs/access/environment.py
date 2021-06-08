"""Class for loading environment"""
import logging
import os

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class VariableTree:
    def __init__(self, root):
        self._root = root

    def __repr__(self):
        return str(self._root)

    @classmethod
    def from_environment(cls, separator=None):
        ''' Generate a VariableTree from all current environment variables. '''
        separator = separator or '__'

        # pylint: disable=protected-access
        return cls.generate(os.environ._data, separator)

    @classmethod
    def generate(cls, variables, separator=None):
        root = dict()

        for key, value in (cls._decode_kv_pair(k, v) for k, v in variables.items()):
            cls._create_branch(root, key, value, separator)

        return VariableTree(root)

    @classmethod
    def _decode_kv_pair(cls, key, value):
        decoded_kv_pair = [key, value]

        for index, item in enumerate((key, value)):
            if hasattr(item, 'decode'):
                decoded_kv_pair[index] = item.decode('utf8')

        return tuple(decoded_kv_pair)

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
    def _create_branch(cls, trunk, name, value, separator):
        LOGGER.debug('Name: %s', name)
        if separator in name:
            prefix, suffix = name.split(separator, 1)
            LOGGER.debug('Prefix: %s\tSuffix: %s', prefix, suffix)

            if prefix not in trunk:
                trunk[prefix] = dict(
                    branches=dict(),
                    value=None,
                )

            if prefix and suffix:
                cls._create_branch(trunk[prefix]['branches'], suffix, value, separator)
        else:
            if name not in trunk:
                trunk[name] = dict(
                    branches=dict(),
                    value=None,
                )

            trunk[name]['value'] = value
