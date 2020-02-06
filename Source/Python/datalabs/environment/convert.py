from abc import ABC, abstractmethod
import logging

import jinja2

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class CondaEnvironmentConverter(ABC):
    def __init__(self, conda_package_list_filename, template_filename):
        self._conda_package_list_filename = conda_package_list_filename
        self._template_filename

    def convert(self) -> str:
        conda_dependencies = None
        template = None
        converted_dependencies = None

        try:
            conda_dependencies = self.read_conda_dependencies(self._conda_package_list_filename)
        except FileNotFoundError as fnfe:
            logger.exception(f'Unable to find conda package list file {self._conda_package_list_filename}.')

        try:
            template = self.read_template(self._template_filename)
        except FileNotFoundError as fnfe:
            logger.exception(f'Unable to find template file {self._template_filename}.')

        if conda_dependencies and pipfile_template:
            converted_dependencies = self.render_template(template, conda_dependencies)

        return converted_dependencies

    def read_conda_dependencies(cls, conda_package_list_filename):
        dependencies = {}

        with open(conda_package_list_filename) as file:
            for line in file:
                variable, value = cls.parse_conda_dependency(line)

                if variable:
                    dependencies[variable] = value

        return dependencies

    def read_pipfile_template(cls, template_filename):
        template = None

        with open(template_filename) as file:
            template = jinja2.Template(file.read())

        return template

    def parse_conda_dependency(cls, dependency):
        variable = None
        value = None

        if not dependency.startswith('#'):
            variable, value, _ = dependency.split('=')

        return variable, value

    @abstractmethod
    def render_template(template: jinja2.Template, conda_dependencies: dict) -> str:
        pass

class Conda2PipenvEnvrionmentConverter(CondaEnvironmentConverter):
    def render_template(template, conda_dependencies):
    names = sorted(conda_dependencies.keys())
    pipfile_dependencies = []
    python_version

    for name in names:
        if name == 'python':
            python_version = conda_dependencies[name]
        elif name == 'conda':
            pass
        else:
            pipfile_dependencies.append(f"name = '=={conda_dependencies[name]}'")

    return pipfile_template.render(packages=pipfile_dependencies, python_version=python_version)
