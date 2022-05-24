"""Access environmental parameters as references from other parameters"""
import logging
import os
import re

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


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
        environment = os.environ.items()

        return {key:value for key, value in environment if re.match(r'.*\$\{[^${}]+\}', value, re.DOTALL) is None}

    @classmethod
    def _get_reference_variables(cls, environment):
        LOGGER.debug("Getting reference variables from the following environment: %s", environment)
        return {key:value for key, value in environment.items() if re.match(r'.*\$\{[^${}]+\}', value, re.DOTALL)}

    def _resolve_references_variables(self, variables, parameters):
        for key, value in variables.items():
            resolved_value = None

            try:
                resolved_value = self._resolve_references_in_value(value, parameters)
            except KeyError:
                LOGGER.warning('Ignoring bad environment variable reference(s) in %s', key)

            if resolved_value is not None:
                variables[key] = resolved_value

        return variables

    def _resolve_references_in_value(self, value, parameters):
        match_count = 0
        match = re.match(r'.*\$\{([^${}]+)\}', value, re.DOTALL)

        while match is not None and match_count < self._match_limit:
            match_count += 1
            match_value = match.group(1)
            value = value.replace('${'+match_value+'}', str(parameters[match_value]))

            match = re.match(r'.*\$\{([^${}]+)\}', value, re.DOTALL)

        return value
