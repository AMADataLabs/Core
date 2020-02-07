from abc import ABC, abstractmethod
import logging

import jinja2

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class CondaEnvironmentConverter(ABC):
    def __init__(self, conda_package_list_filename, template_filename):
        self._conda_package_list_filename = conda_package_list_filename
        self._template_filename = template_filename

    def convert(self) -> str:
        conda_dependencies = None
        template = None
        converted_dependencies = None

        try:
            conda_dependencies = self._read_conda_dependencies(self._conda_package_list_filename)
        except FileNotFoundError as fnfe:
            logger.exception(f'Unable to find conda package list file {self._conda_package_list_filename}.')

        try:
            template = self._read_template(self._template_filename)
        except FileNotFoundError as fnfe:
            logger.exception(f'Unable to find template file {self._template_filename}.')

        if conda_dependencies and template:
            converted_dependencies = self._render_template(template, conda_dependencies)

        return converted_dependencies

    @classmethod
    def _read_conda_dependencies(cls, conda_package_list_filename):
        dependencies = {}

        with open(conda_package_list_filename) as file:
            for line in file:
                variable, value = cls._parse_conda_dependency(line)

                if variable:
                    dependencies[variable] = value

        return dependencies

    @classmethod
    def _read_template(cls, template_filename):
        template = None

        with open(template_filename) as file:
            template = jinja2.Template(file.read())

        return template

    @classmethod
    def _parse_conda_dependency(cls, dependency):
        variable = None
        value = None

        if not dependency.startswith('#'):
            variable, value, _ = dependency.split('=')

        return variable, value

    @classmethod
    @abstractmethod
    def _render_template(cls, template: jinja2.Template, conda_dependencies: dict) -> str:
        pass

class Conda2PipenvEnvrionmentConverter(CondaEnvironmentConverter):
    @classmethod
    def _render_template(cls, template, conda_dependencies):
        names = sorted(conda_dependencies.keys())
        pipfile_dependencies = []
        python_version = None

        for name in names:
            if name == 'python':
                python_version = conda_dependencies[name]
            elif name == 'conda':
                pass
            else:
                pipfile_dependencies.append(f"{name} = '=={conda_dependencies[name]}'")

        return template.render(packages=pipfile_dependencies, python_version=python_version)
