""" Resolve task class name using the configured DAG class. """
from   dataclasses import dataclass
import os
import sys
import tempfile

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
    def get_task_class(cls, task_parameters):
        event_type = task_parameters["type"]
        getter_method = None

        try:
            getter_method = getattr(cls, f'_get_{event_type.lower()}_class')
        except AttributeError as exception:
            raise ValueError(f"Invalid DAG plugin event type '{event_type}'") from exception

        return getter_method(task_parameters)

    # pylint: disable=unused-argument
    @classmethod
    def _get_dag_class(cls, task_parameters):
        return DAGTask

    @classmethod
    def _get_task_class(cls, task_parameters):
        raise NotImplementedError('Dynamic DAG task resolver only supports the "DAG" task.')


class DAGTask(task.Task):
    def run(self):
        dag_class, dag = [d.decode() for d in self._data]
        dag_executor = LocalDAGExecutorTask(
            {
                "dag_class": dag_class,
                "task_statuses": self._parameters["task_statuses"]
            }
        )

        with tempfile.TemporaryDirectory() as python_path:
            self._write_dag(dag_class, dag, python_path)

            sys.path.append(python_path)

            dag_executor.run()

    @classmethod
    def _write_dag(cls, dag_class, dag, python_path):
        package, module, class_name = dag_class.rsplit(dag_class, 2)
        package_path = os.path.join(*package.split("."))
        init_path = os.path.join(package_path, "__init__.py")
        module_path = os.path.join(package_path, f"{module}.py")

        os.makedirs(os.path.join(python_path, package_path))

        with open(init_path, "w"):
            pass

        with open(module_path, "w") as file:
            file.write(dag)



