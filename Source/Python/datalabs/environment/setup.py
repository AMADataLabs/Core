""" Project environment setup. """

import bisect
from   dataclasses import dataclass
import logging

import datalabs.common.setup as setup

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@dataclass
class EnvironmentFilenames(setup.FileGeneratorFilenames):
    package_list: str
    whitelist: str


# pylint: disable=abstract-method
class EnvironmentGenerator(setup.TemplatedFileGenerator):
    @classmethod
    def create(cls, args):
        validated_args = cls._validate_args(args)
        environment = validated_args['env']
        filenames = setup.GeneratorFilenames(
            package_list=validated_args['in'],
            template=validated_args['template'],
            configuration=validated_args['out'],
            whitelist=validated_args.get('whitelist')
        )
        python_version = validated_args['python']

        return ENVIRONMENT_GENERATORS[environment](filenames, python_version)

    @classmethod
    def _validate_args(cls, args):
        if args['env'] not in ENVIRONMENT_GENERATORS:
            raise ValueError(f'Unsupported environment "{args["env"]}"')

        return args

    def _read_dependencies(self):
        dependencies = {}
        whitelist = self._read_whitelist()

        with open(self._filenames.package_list) as file:
            for line in file:
                variable, value = self._parse_dependency(line)

                if variable and (whitelist is None or variable in whitelist):
                    dependencies[variable] = value

        return dependencies

    def _read_whitelist(self):
        whitelist = None

        if self._filenames.whitelist:
            LOGGER.debug('Whitelist Filename: %s', self._filenames.whitelist)
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


class PipEnvironmentGenerator(EnvironmentGenerator):
    def _generate_template_parameters(self):
        dependencies = self._read_dependencies()

        sorted_dependencies = self._sort_dependencies(dependencies)

        return self._generate_template_parameter_dictionary(sorted_dependencies)

    @classmethod
    def _sort_dependencies(cls, dependencies):
        names = sorted(dependencies.keys())
        sorted_dependencies = []

        for name in names:
            sorted_dependencies.append((name, dependencies[name]))

        return sorted_dependencies

    # pylint: disable=no-self-use
    def _generate_template_parameter_dictionary(self, sorted_dependencies):
        return dict(package_versions=sorted_dependencies)


class PipenvEnvironmentGenerator(PipEnvironmentGenerator):
    def _generate_template_parameter_dictionary(self, sorted_dependencies):
        return dict(package_versions=sorted_dependencies, python_version=self._parameters['python_version'])


class CondaEnvironmentGenerator(PipEnvironmentGenerator):
    def _generate_template_parameters(self):
        dependencies = self._read_dependencies()

        sorted_dependencies = self._sort_dependencies(dependencies)

        sorted_dependencies = self._insert_python_dependency(sorted_dependencies)

        return self._generate_template_parameter_dictionary(sorted_dependencies)

    def _insert_python_dependency(self, dependencies):
        python_dependency = ('python', self._parameters['python_version'])

        bisect.insort(dependencies, python_dependency)

        return dependencies


ENVIRONMENT_GENERATORS = {
    'pip': PipEnvironmentGenerator,
    'pipenv': PipenvEnvironmentGenerator,
    'conda': CondaEnvironmentGenerator,
}
