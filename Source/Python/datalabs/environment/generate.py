from abc import ABC, abstractmethod
from collections import namedtuple
import logging

import jinja2

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


GeneratorFilenames = namedtuple(
    'GeneratorFilenames',
    'package_list template whitelist configuration'
)


class EnvironmentGenerator(ABC):
    def __init__(self, filenames: GeneratorFilenames, python_version) -> str:
        self._filenames = filenames
        self._python_version = python_version

    def generate(self) -> str:
        dependencies = None
        template = None
        converted_dependencies = None

        dependencies = self._read_dependencies()

        template = self._read_template()

        if dependencies and template:
            converted_dependencies = self._render_template(template, dependencies)

            self._write_converted_dependencies(converted_dependencies)

    def _read_dependencies(self):
        dependencies = {}
        whitelist = self._read_whitelist()

        with open(self._filenames.package_list) as file:
            for line in file:
                variable, value = self._parse_dependency(line)

                if variable and (whitelist is None or variable in whitelist):
                    dependencies[variable] = value

        return dependencies

    def _read_template(self):
        template = None

        with open(self._filenames.template) as file:
            template = jinja2.Template(file.read())

        return template

    def _read_whitelist(self):
        whitelist = None

        if self._filenames.whitelist:
            logger.debug(f'Whitelist Filename: {self._filenames.whitelist}')
            with open(self._filenames.whitelist) as file:
                whitelist_line = file.readline().strip()

            whitelist = whitelist_line.split(',')

        return whitelist

    @classmethod
    def _parse_dependency(cls, dependency):
        variable = None
        value = None

        if not dependency.startswith('#'):
            variable, value = dependency.strip().split('==')

        return variable, value

    @classmethod
    @abstractmethod
    def _render_template(cls, template: jinja2.Template, dependencies: dict) -> str:
        pass

    def _write_converted_dependencies(self, converted_dependencies):
        with open(self._filenames.configuration, 'w') as file:
            file.write(converted_dependencies)
            file.flush()


class PipenvEnvironmentGenerator(EnvironmentGenerator):
    def _render_template(self, template, dependencies):
        names = sorted(dependencies.keys())
        pipfile_dependencies = []
        python_version = None

        for name in names:
            pipfile_dependencies.append(f"{name} = '=={dependencies[name]}'")

        return template.render(packages=pipfile_dependencies, python_version=self._python_version)


class CondaEnvironmentGenerator(EnvironmentGenerator):
    def _render_template(self, template, dependencies):
        names = sorted(dependencies.keys())
        pipfile_dependencies = []
        python_version = None

        pipfile_dependencies.append(f"python={self._python_version}")

        for name in names:
            if name != 'python':
                pipfile_dependencies.append(f"{name}={dependencies[name]}")

        return template.render(packages=pipfile_dependencies)
