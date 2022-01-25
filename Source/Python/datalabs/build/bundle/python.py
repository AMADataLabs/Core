""" Python source file bundle class to aid in packaging apps. """
import logging
import os

from   datalabs.build.bundle.base import SourceBundle

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class PythonSourceBundle(SourceBundle):
    @classmethod
    def _find_package_files(cls, package, base_path):
        filtered_files = super()._find_package_files(package, base_path)
        relative_package_path = cls._generate_package_path(package['package'])
        init_path = os.path.join(relative_package_path, '__init__.py')

        if init_path not in filtered_files:
            filtered_files.append(init_path)

        return filtered_files
