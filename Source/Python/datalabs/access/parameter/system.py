"""Access environmental parameters as references from other parameters"""
import logging
import os
import re

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class ReferenceEnvironmentLoader:
    ''' Resolve environment variable values that contain references to other variables. '''
    def __init__(self, parameters: dict, limit=50):
        self._parameters = parameters
        self._match_limit = limit

    def load(self, environment: dict = None):
        if self._parameters:
            environment = environment or os.environ
            reference_variables = self._get_reference_variables(environment)

            resolved_reference_variables = self._resolve_references_variables(reference_variables, self._parameters)

            environment.update(resolved_reference_variables)

    @classmethod
    def from_environ(cls, limit=50):
        parameters = cls._get_referent_variables()

        return ReferenceEnvironmentLoader(parameters, limit=limit)

    @classmethod
    def _get_referent_variables(cls):
        return {key:value for key, value in os.environ.items() if re.match(r'.*\$\{[^${}]+\}', value) is None}

    @classmethod
    def _get_reference_variables(cls, environment):
        return {key:value for key, value in environment.items() if re.match(r'.*\$\{[^${}]+\}', value)}

    def _resolve_references_variables(self, variables, parameters):
        for key, value in variables.items():
            variables[key] = self._resolve_references_in_value(value, parameters)

        return variables

    def _resolve_references_in_value(self, value, parameters):
        match_count = 0
        match = re.match(r'.*\$\{([^${}]+)\}', value)

        while match is not None and match_count < self._match_limit:
            match_count += 1
            match_value = match.group(1)
            value = value.replace('${'+match_value+'}', str(parameters[match_value]))

            match = re.match(r'.*\$\{([^${}]+)\}', value)

        return value
