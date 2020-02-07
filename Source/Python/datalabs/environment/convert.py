from abc import ABC, abstractmethod
import logging

import jinja2

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class CondaEnvironmentConverter(ABC):
    def __init__(self, conda_package_list_filename: str, template_filename: str, whitelist_filename: str=None) -> str:
        self._conda_package_list_filename = conda_package_list_filename
        self._template_filename = template_filename
        self._whitelist_filename = whitelist_filename

    def convert(self) -> str:
        conda_dependencies = None
        template = None
        converted_dependencies = None

        try:
            conda_dependencies = self._read_conda_dependencies()
        except FileNotFoundError as fnfe:
            logger.exception(f'Unable to find conda package list file {self._conda_package_list_filename}.')

        try:
            template = self._read_template()
        except FileNotFoundError as fnfe:
            logger.exception(f'Unable to find template file {self._template_filename}.')

        if conda_dependencies and template:
            converted_dependencies = self._render_template(template, conda_dependencies)

        return converted_dependencies

    def _read_conda_dependencies(self):
        dependencies = {}
        whitelist = self._read_whitelist()

        with open(self._conda_package_list_filename) as file:
            for line in file:
                variable, value = self._parse_conda_dependency(line)

                if variable and (whitelist is None or variable in whitelist):
                    dependencies[variable] = value

        return dependencies

    def _read_template(self):
        template = None

        with open(self._template_filename) as file:
            template = jinja2.Template(file.read())

        return template

    def _read_whitelist(self):
        whitelist = None

        if self._whitelist_filename:
            logger.debug(f'Whitelist Filename: {self._whitelist_filename}')
            with open(self._whitelist_filename) as file:
                whitelist_line = file.readline().strip()

            whitelist = whitelist_line.split(',')

        return whitelist

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
