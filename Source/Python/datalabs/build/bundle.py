import logging
import os

import yaml


logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class SourceBundle:
    def __init__(self, modspec_path):
        self._modspec_path = modspec_path

    def files(self, base_path):
        modspec_yaml = self._load_module_spec(self._modspec_path)

        modspec = self._parse_module_spec(modspec_yaml)

        return self._generate_module_paths(modspec, base_path)

    @classmethod
    def _load_module_spec(cls, modspec_path) -> str:
        LOGGER.debug(f'Modspec path: {modspec_path}')
        modspec_yaml = None

        with open(modspec_path, 'r') as file:
            modspec_yaml = file.read()

        return modspec_yaml

    @classmethod
    def _parse_module_spec(cls, modspec_yaml) -> dict:
        modspec = yaml.safe_load(modspec_yaml)
        LOGGER.debug(f'Module spec: {modspec}')

        return modspec

    @classmethod
    def _generate_module_paths(cls, modspec, base_path):
        package_file_lists = []

        for package in modspec['modspec']:
            package_file_lists.append(cls._find_package_files(package, base_path))

        return [file for package_files in package_file_lists for file in package_files]

    @classmethod
    def _find_package_files(cls, package, base_path):
        package_path = cls._generate_package_path(package['package'], base_path)
        init_path = os.path.join(package_path, '__init__.py')
        filtered_files = None
        _, _, all_files = next(os.walk(package_path))

        if 'include' in package:
            filtered_files = [os.path.join(package_path, f) for f in all_files if f.split('.')[0] in package['include']]
        elif 'exclude' in package:
            filtered_files = [os.path.join(package_path, f) for f in all_files if f.split('.')[0] not in package['exclude']]
        else:
            filtered_files = [os.path.join(package_path, f) for f in all_files]

        if init_path not in filtered_files:
            filtered_files.append(init_path)

        return filtered_files

    @classmethod
    def _generate_package_path(cls, package, base_path):
        packages = package.split('.')

        return os.path.join(base_path, 'Source', 'Python', *packages)
