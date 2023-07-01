""" Helper class that converts flat-format DAG configuration YAML files to hierarchical format. """
from   collections import defaultdict
import logging
import sys

import argparse
import yaml
from   yaml.representer import Representer

from   datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class ConfigurationFileConverter(Task):
    def run(self):
        hierarchical_document = None

        with open(self._parameters["file"], encoding='utf-8') as file:
            flat_document = yaml.safe_load(file.read())

        hierarchical_document = self._convert(flat_document)

        yaml.add_representer(defaultdict, Representer.represent_dict)

        converted_yaml = yaml.dump(hierarchical_document, indent=4, explicit_start=True)

        if self._parameters["dry_run"]:
            print(converted_yaml)
        else:
            with open(self._parameters["file"], "w", encoding="utf8") as file:
                file.write(converted_yaml)

    @classmethod
    def _convert(cls, flat_document):
        dag = None
        hierarchical_parameters = defaultdict(dict)

        for flat_parameter in flat_document["data"]:
            dag, task, parameter = cls._split_parameter_name(flat_parameter)

            hierarchical_parameters[task][parameter] = flat_document["data"][flat_parameter]

        for task_parameters in hierarchical_parameters:
            cls._replace_dag_state_parameters(hierarchical_parameters[task_parameters])

        return {dag: hierarchical_parameters}

    @classmethod
    def _split_parameter_name(cls, flat_parameter):
        dag = None
        task = "GLOBAL"
        parameter = flat_parameter

        if "__" in flat_parameter:
            dag, task, parameter = flat_parameter.split('__')

        return dag, task, parameter

    @classmethod
    def _replace_dag_state_parameters(cls, parameters):
        if "DAG_STATE_TABLE" in  parameters:
            parameters["DAG_STATE"] = dict(
                CLASS=parameters.pop("DAG_STATE_CLASS"),
                STATE_TABLE=parameters.pop("DAG_STATE_TABLE"),
                LOCK_TABLE=parameters.pop("STATE_LOCK_TABLE")
            )


# pylint: disable=broad-except
def main():
    return_code = 0

    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('-d', '--dry-run', action="store_true", help='configuration file path')
    argument_parser.add_argument('file', help='configuration file path')
    command_line_arguments = vars(argument_parser.parse_args())

    try:
        ConfigurationFileConverter(command_line_arguments).run()
    except Exception:
        LOGGER.exception('Failed to convert configuration file %s.', command_line_arguments["file"])
        return_code = 1

    sys.exit(return_code)


if __name__ == "__main__":
    main()
