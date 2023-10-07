""" Helper class that loads DAG configuration from a YAML file into the environment. """
from   dataclasses import dataclass
import json
import logging
import os
import yaml

from   datalabs.access.parameter.system import ReferenceEnvironmentLoader
from   datalabs.parameter import add_schema, ParameterValidatorMixin
from   datalabs.plugin import import_plugin

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class ParameterExtractorMixin:
    def _get_parameters_from_file(self, config_file, dag, task):
        dag_from_file, variables = self._extract_variables_from_config([config_file])

        parameters = self._parse_variables(variables)

        if dag != dag_from_file:
            raise ValueError("Requested DAG " + dag + " does not match the config file DAG " + dag_from_file)

        parameters = self._expand_macros(parameters)

        if "GLOBAL" in parameters:
            ReferenceEnvironmentLoader(parameters["GLOBAL"]).load(environment=parameters[task])

        return parameters[task]

    @classmethod
    def _extract_variables_from_config(cls, filenames):
        config = {}
        dag = None

        for filename in filenames:
            with open(filename, encoding='utf-8') as file:
                document = yaml.safe_load(file.read())
                dag = list(document)[0]

                config.update(document[dag])

        return dag, config

    def _parse_variables(self, variables, top_level=True):
        parameters = variables

        if isinstance(variables, dict):
            for key, value in variables.items():
                if isinstance(value, dict):
                    parameters[key] =  self._parse_variables(value, top_level=False)

                    if not top_level:
                        parameters[key] = json.dumps(parameters[key])

        return parameters

    @classmethod
    def _expand_macros(cls, parameters):
        parameters = cls._expand_task_parameters(parameters)

        if "DAG" in parameters:
            try:
                parameters = cls._add_task_classes(parameters)
            except ModuleNotFoundError:
                LOGGER.warning("Unable to add TASK_CLASS due to missing DAG %s", parameters["DAG"]["DAG_CLASS"])

        return parameters

    @classmethod
    def _expand_task_parameters(cls, parameters):
        deleted_tasks = []
        expanded_task_parameters = []

        for task, task_parameters in parameters.items():
            if '__MACRO_COUNT__' in task_parameters:
                deleted_tasks.append(task)

                expanded_task_parameters += cls._generate_macro_parameters(task, task_parameters)

        for task in deleted_tasks:
            parameters.pop(task)

        for task_parameters in expanded_task_parameters:
            parameters.update(task_parameters)

        return parameters

    @classmethod
    def _add_task_classes(cls, parameters):
        dag_class = import_plugin(parameters["DAG"]["DAG_CLASS"])


        for task, task_parameters in parameters.items():
            if task not in ("GLOBAL", "DAG") and "TASK_CLASS" not in task_parameters:
                parameters[task] = cls._add_task_class(dag_class, task, task_parameters)

        for task in dag_class.tasks:
            if task not in parameters:
                parameters[task] = cls._add_task_class(dag_class, task, {})

        return parameters

    @classmethod
    def _generate_macro_parameters(cls, task, task_parameters):
        count = int(task_parameters['__MACRO_COUNT__'])
        generated_parameters = []


        for index in range(count):
            instance_parameters = {
                name: cls._replace_macro_parameters(value, count, index) for name, value in task_parameters.items()
                if name != '__MACRO_COUNT__'
            }

            generated_parameters.append({f'{task}_{index}': instance_parameters})

        return generated_parameters

    @classmethod
    def _add_task_class(cls, dag_class, task, task_parameters):
        task_class = dag_class.task_class(task)
        task_class_name = task_class

        if hasattr(task_class, "name"):
            task_class_name = task_class.name

        task_parameters["TASK_CLASS"] = task_class_name

        return task_parameters

    @classmethod
    def _generate_item(cls, dag, task, variables):
        item = dict(
            Task=dict(S=task),
            DAG=dict(S=dag),
            Variables=dict(S=json.dumps(variables))
        )

        return item

    @classmethod
    def _replace_macro_parameters(cls, value, macro_count, macro_index):
        resolved_value = value

        if hasattr(value, 'replace'):
            resolved_value = value.replace('__MACRO_COUNT__', str(macro_count))
            resolved_value = resolved_value.replace('__MACRO_INDEX__', str(macro_index))

        return resolved_value


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class FileEnvironmentParameters:
    path: str
    dag: str
    task: str


class FileEnvironmentLoader(ParameterExtractorMixin, ParameterValidatorMixin):
    PARAMETER_CLASS = FileEnvironmentParameters

    def __init__(self, parameters):
        self._parameters = self._get_validated_parameters(parameters)

    def load(self, environment: dict = None):
        if environment is None:
            environment = os.environ

        task_parameters = self._get_parameters_from_file(
            self._parameters.path,
            self._parameters.dag,
            self._parameters.task
        )

        environment.update(task_parameters)


class FileTaskParameterGetterMixin:
    # pylint: disable=redefined-outer-name
    @classmethod
    def _get_dag_task_parameters_from_file(cls, dag: str, task: str, config_file):
        file_loader = FileEnvironmentLoader(dict(
            dag=dag,
            task=task,
            path=config_file
        ))
        parameters = {}

        file_loader.load(parameters)

        return parameters
