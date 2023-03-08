""" Python source file bundle class to aid in packaging apps. """
import itertools
import logging
import os
import shutil

import yaml


logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class SourceBundle:
    def __init__(self, modspec_yaml):
        self._modspec_yaml = modspec_yaml

    @classmethod
    def from_file(cls, modspec_path):
        LOGGER.info('Modspec path: %s', modspec_path)
        modspec_yaml = None

        with open(modspec_path, 'r', encoding="utf-8") as file:
            modspec_yaml = file.read()

        return cls(modspec_yaml)

    def copy(self, base_path, app_path):
        relative_file_paths, shared_source_paths, app_source_paths = self._generate_copy_paths(base_path, app_path)

        self._copy_files(shared_source_paths, app_source_paths)

        return relative_file_paths

    def copy_multiple(self, base_paths: list, app_path):
        all_relative_file_paths = []
        all_shared_source_paths = []
        all_app_source_paths = []

        for base_path in base_paths:
            relative_file_paths, shared_source_paths, app_source_paths = self._generate_copy_paths(base_path, app_path)

            all_relative_file_paths += relative_file_paths
            all_shared_source_paths += shared_source_paths
            all_app_source_paths += app_source_paths

        self._copy_files(all_shared_source_paths, all_app_source_paths)

        return all_relative_file_paths

    def files(self, base_path):
        modspec = self._parse_module_spec(self._modspec_yaml)

        return self._generate_module_paths(modspec, base_path)

    def _generate_copy_paths(self, base_path, app_path):
        shared_source_path = os.path.join(base_path)
        relative_file_paths = self.files(shared_source_path)
        shared_source_paths = [os.path.join(shared_source_path, p) for p in relative_file_paths]
        app_source_paths = [os.path.join(app_path, p) for p in relative_file_paths]

        return relative_file_paths, shared_source_paths, app_source_paths

    @classmethod
    def _copy_files(cls, source_paths, target_paths):
        for source_path, target_path in zip(source_paths, target_paths):
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            shutil.copyfile(source_path, target_path)

    @classmethod
    def _parse_module_spec(cls, modspec_yaml) -> dict:
        modspec = yaml.safe_load(modspec_yaml)
        LOGGER.debug('Module spec: %s', modspec)

        return modspec

    @classmethod
    def _generate_module_paths(cls, modspec, base_path):
        package_file_lists = []

        packages = cls._add_missing_parent_packages(modspec['modspec'])

        for package in packages:
            package_file_lists.append(cls._find_package_files(package, base_path))

        return [file for package_files in package_file_lists for file in package_files]

    @classmethod
    def _add_missing_parent_packages(cls, packages):
        package_names = [package["package"] for package in packages]

        for package_name in package_names:
            components = package_name.split('.')

            parent_package_names = list(itertools.accumulate(components, lambda x, y: '.'.join((x, y))))

            packages = cls._add_missing_packages_by_name(packages, package_names, parent_package_names)

        return sorted(packages, key=lambda x: x["package"])

    @classmethod
    def _add_missing_packages_by_name(cls, packages, package_names, parent_package_names):
        for name in parent_package_names:
            if name not in package_names:
                packages.append(dict(package=name))

        return packages


    @classmethod
    def _find_package_files(cls, package, base_path):
        relative_package_path = cls._generate_package_path(package['package'])
        absolute_package_path = os.path.join(base_path, relative_package_path)
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
            LOGGER.warning('Unable to find package files in directory %s.', path)

        return all_files
