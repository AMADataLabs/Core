""" Resolve the trigger handler class name using SNS topic map parameters. """
from   dataclasses import dataclass

from   datalabs.parameter import add_schema, ParameterValidatorMixin
from   datalabs.plugin import import_plugin
from   datalabs import task


@add_schema(unknowns=True)
@dataclass
class TaskResolverParameters:
    handler: str
    unknowns: dict=None


class TaskResolver(ParameterValidatorMixin, task.TaskResolver):
    PARAMETER_CLASS = TaskResolverParameters

    @classmethod
    def get_task_class(cls, runtime_parameters):
        return import_plugin(runtime_parameters["handler_class"])
