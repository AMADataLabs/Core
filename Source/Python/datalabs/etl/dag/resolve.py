""" Resolve task class name using the configured DAG class. """
from   dataclasses import dataclass
import os

from   datalabs.etl.dag.task import DAGExecutorTask
import datalabs.task as task
from   datalabs.parameter import add_schema, ParameterValidatorMixin
from   datalabs.plugin import import_plugin


@add_schema
@dataclass
class TaskResolverParameters:
    type: str
    execution_time: str
    task: str=None


class TaskResolver(ParameterValidatorMixin, task.TaskResolver):
    PARAMETER_CLASS = TaskResolverParameters

    @classmethod
    def get_task_class(cls, parameters):
        parameters = cls._get_validated_parameters(parameters)
        task_class = None

        if parameters.type == "DAG":
            task_class = DAGExecutorTask
        elif parameters.type == "Task":
            dag_class = import_plugin(os.environ.get('DAG_CLASS'))
            task_class = dag_class.task_class(parameters.task)
        else:
            raise ValueError(f"Invalid DAG plugin event type '{parameters.type}'")

        return task_class
