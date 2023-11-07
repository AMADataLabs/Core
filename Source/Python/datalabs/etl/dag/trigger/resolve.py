""" Resolve the trigger handler class name using SNS topic map parameters. """
from   dataclasses import dataclass

from   datalabs.parameter import add_schema, ParameterValidatorMixin
from   datalabs.plugin import import_plugin
from   datalabs import task


class TaskResolver(ParameterValidatorMixin, task.TaskResolver):
    @classmethod
    def get_task_class(cls, task_parameters):
        return import_plugin(task_parameters["handler_class"])
