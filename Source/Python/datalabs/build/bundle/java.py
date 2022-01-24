""" Java source file bundle class to aid in packaging apps. """
import logging
import os
import shutil

import yaml

from   datalabs.build.bundle.base import SourceBundle


logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class JavaSourceBundle(SourceBundle):
    @classmethod
    def _generate_module_paths(cls, modspec, base_path):
        module_paths = super()._generate_module_paths(modspec, base_path)
        task_package_path = os.path.join('datalabs', 'task')
        lambda_function_path = os.path.join(base_path, task_package_path, 'LambdaFunction.java')
        local_process_path = os.path.join(base_path, task_package_path, 'LocalProcess.java')

        if lambda_function_path not in module_paths:
            module_paths.append(lambda_function_path)

        if local_process_path not in module_paths:
            module_paths.append(local_process_path)

        return module_paths
