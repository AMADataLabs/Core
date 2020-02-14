""" Common classes for doing project setup tasks. """

from   abc import ABC, abstractmethod
from   dataclasses import dataclass

from   jinja2 import Template


@dataclass
class FileGeneratorFilenames:
    template: str
    output: str


class TemplatedFileGenerator(ABC):
    def __init__(self, filenames: FileGeneratorFilenames, **parameters):
        self._filenames = filenames
        self._parameters = parameters

    def generate(self) -> str:
        template = self._read_template()

        template_parameters = self._generate_template_parameters()

        output = self._render_template(template, template_parameters)

        self._write_output(output)

    def _read_template(self) -> Template:
        template = None

        with open(self._filenames.template) as file:
            template = Template(file.read())

        return template

    @abstractmethod
    def _generate_template_parameters(self) -> dict:
        pass

    @classmethod
    def _render_template(cls, template: Template, template_paratameters: dict) -> str:
        return template.render(**template_paratameters)

    def _write_output(self, output):
        with open(self._filenames.output, 'w') as file:
            file.write(output)
            file.flush()


class SimpleFileGenerator(TemplatedFileGenerator):
    def _generate_template_parameters(self):
        return self._parameters
