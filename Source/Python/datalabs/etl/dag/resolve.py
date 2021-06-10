""" Resolve task class name using the configured DAG class. """
from   dataclasses import dataclass

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
    def get_task_class_name(cls, parameters):
        self._parameters = self._get_validated_parameters(parameters)
        task_class_name = None

        if type == "DAG":
            task_class_name = 'datalabs.etl.dag.task.DAGExecutorTask'
        elif type == "Task":
            dag_class = import_plugin(cls.DAG_CLASS)
            dag = dag_class(dict(DAG_CLASS=cls.DAG_CLASS, STATE_CLASS=None))
            task_class_name = dag_class.TASK_CLASSES[task]
        else:
            raise ValueError(f"Invalid DAG plugin event type '{type}'")

        return task_class_name
