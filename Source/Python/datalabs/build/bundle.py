""" Python source file bundle class to aid in packaging apps. """
import logging
import os
import shutil

import yaml


logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class SourceBundle:
    def __init__(self, modspec_path):
        self._modspec_path = modspec_path

    def copy(self, base_path, app_path):
        shared_source_path = os.path.join(base_path)
        relative_file_paths = self.files(shared_source_path)
        shared_source_paths = [os.path.join(shared_source_path, p) for p in relative_file_paths]
        app_source_paths = [os.path.join(app_path, p) for p in relative_file_paths]

        for source_file, destination_file in zip(shared_source_paths, app_source_paths):
            os.makedirs(os.path.dirname(destination_file), exist_ok=True)
            shutil.copyfile(source_file, destination_file)

        return relative_file_paths

    def files(self, base_path):
        modspec_yaml = self._load_module_spec(self._modspec_path)

        modspec = self._parse_module_spec(modspec_yaml)

        return self._generate_module_paths(modspec, base_path)

    @classmethod
    def _load_module_spec(cls, modspec_path) -> str:
        LOGGER.debug('Modspec path: %s', modspec_path)
        modspec_yaml = None

        with open(modspec_path, 'r') as file:
            modspec_yaml = file.read()

        return modspec_yaml

    @classmethod
    def _parse_module_spec(cls, modspec_yaml) -> dict:
        modspec = yaml.safe_load(modspec_yaml)
        LOGGER.debug('Module spec: %s', modspec)

        return modspec

    @classmethod
    def _generate_module_paths(cls, modspec, base_path):
        package_file_lists = []

        for package in modspec['modspec']:
            package_file_lists.append(cls._find_package_files(package, base_path))

        return [file for package_files in package_file_lists for file in package_files]

    @classmethod
    def _find_package_files(cls, package, base_path):
        relative_package_path = cls._generate_package_path(package['package'])
        absolute_package_path = os.path.join(base_path, relative_package_path)
        init_path = os.path.join(relative_package_path, '__init__.py')
        filtered_files = None
        all_files = cls._get_files_in_directory(absolute_package_path)

        if 'include' in package:
            filtered_files = [
                os.path.join(relative_package_path, f) for f in all_files if f.split('.')[0] in package['include']
            ]
        elif 'exclude' in package:
            filtered_files = [
                os.path.join(relative_package_path, f) for f in all_files if f.split('.')[0] not in package['exclude']
            ]
        else:
            filtered_files = [os.path.join(relative_package_path, f) for f in all_files]

        if init_path not in filtered_files:
            filtered_files.append(init_path)

        return filtered_files

    @classmethod
    def _generate_package_path(cls, package):
        packages = package.split('.')

        return os.path.join(*packages)

    @classmethod
    def _get_files_in_directory(cls, path):
        LOGGER.debug('Files path: %s', path)
        all_files = []

        try:
            _, _, all_files = next(os.walk(path))
        except StopIteration:
            LOGGER.warning('Unable to to find package files in directory %s.', path)

        return all_files
