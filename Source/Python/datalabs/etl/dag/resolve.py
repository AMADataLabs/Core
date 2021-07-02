""" Resolve task class name using the configured DAG class. """
from   dataclasses import dataclass

from   datalabs.etl.dag.execute import DAGExecutorTask
import datalabs.task as task
from   datalabs.parameter import add_schema, ParameterValidatorMixin


@add_schema(unknowns=True)
@dataclass
class TaskResolverParameters:
    type: str
    dag_class: type
    task: str=None
    unknowns: dict=None


class TaskResolver(ParameterValidatorMixin, task.TaskResolver):
    PARAMETER_CLASS = TaskResolverParameters

    @classmethod
    def get_task_class(cls, parameters):
        parameters = cls._get_validated_parameters(parameters)
        task_class = None

        if parameters.type == "DAG":
            task_class = DAGExecutorTask
        elif parameters.type == "Task":
            task_class = parameters.dag_class.task_class(parameters.task)
        else:
            raise ValueError(f"Invalid DAG plugin event type '{parameters.type}'")

        return task_class
