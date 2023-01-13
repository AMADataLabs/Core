""" Resolve task class name using the configured DAG class. """
from   dataclasses import dataclass

from   datalabs.etl.dag.execute.local import LocalDAGExecutorTask
from   datalabs.parameter import add_schema, ParameterValidatorMixin
from   datalabs.plugin import import_plugin
from   datalabs import task


@add_schema(unknowns=True)
@dataclass
class TaskResolverParameters:
    type: str
    dag_class: str
    task: str=None
    task_class: str=None
    unknowns: dict=None


class TaskResolver(ParameterValidatorMixin, task.TaskResolver):
    PARAMETER_CLASS = TaskResolverParameters

    @classmethod
    def get_task_class(cls, runtime_parameters):
        event_type = runtime_parameters["type"]
        getter_method = None

        try:
            getter_method = getattr(cls, f'_get_{event_type.lower()}_class')
        except AttributeError as exception:
            raise ValueError(f"Invalid DAG plugin event type '{event_type}'") from exception

        return getter_method(runtime_parameters)

    # pylint: disable=unused-argument
    @classmethod
    def _get_dag_class(cls, runtime_parameters):
        return LocalDAGExecutorTask

    @classmethod
    def _get_task_class(cls, runtime_parameters):
        runtime_parameters = cls._get_validated_parameters(runtime_parameters)

        if runtime_parameters.task_class:
            task_class = import_plugin(runtime_parameters.task_class)
        else:
            task_class = cls._get_task_class_from_dag(runtime_parameters.dag_class, runtime_parameters.task)

        return task_class

    @classmethod
    def _get_task_class_from_dag(cls, dag_class, task_name):
        dag_class = import_plugin(dag_class)

        return dag_class.task_class(task_name)
