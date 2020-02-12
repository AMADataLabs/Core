from collections import namedtuple
import logging

import jinja2

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


DockerFilenames = namedtuple(
    'DockerFilenames',
    'template dockerfile'
)


class DockerfileInitializer():
    def __init__(self, filenames: DockerFilenames, project: str) -> str:
        self._filenames = filenames
        self._project = project

    def initialize(self) -> str:
        template = None
        dockerfile = None

        template = self._read_template()

        if template:
            dockerfile = self._render_template(template)

            self._write_dockerfile(dockerfile)

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

    def _write_converted_dependencies(self, converted_dependencies):
        with open(self._filenames.converted_dependencies, 'w') as file:
            file.write(converted_dependencies)
            file.flush()

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
