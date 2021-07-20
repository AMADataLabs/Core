""" Resolve task class name using the configured DAG class. """
from   dataclasses import dataclass
import os

from   datalabs.etl.dag.execute.local import LocalDAGExecutorTask
from   datalabs.parameter import add_schema, ParameterValidatorMixin
from   datalabs.plugin import import_plugin
import datalabs.task as task


@add_schema(unknowns=True)
@dataclass
class TaskResolverParameters:
    type: str
    task: str=None
    unknowns: dict=None


class TaskResolver(ParameterValidatorMixin, task.TaskResolver):
    PARAMETER_CLASS = TaskResolverParameters

    @classmethod
    def get_task_class(cls, parameters):
        parameters = cls._get_validated_parameters(parameters)
        dag_class = import_plugin(os.environ["DAG_CLASS"])
        task_class = None

        if parameters.type == "DAG":
            task_class = LocalDAGExecutorTask
        elif parameters.type == "Task":
            task_class = dag_class.task_class(parameters.task)
        else:
            raise ValueError(f"Invalid DAG plugin event type '{parameters.type}'")

        return task_class
