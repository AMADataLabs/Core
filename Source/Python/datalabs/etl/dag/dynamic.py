""" Resolve task class name using the configured DAG class. """
from   dataclasses import dataclass
import logging
import os
import re
import sys
import tempfile

from   datalabs.etl.dag.execute.local import LocalDAGExecutorTask
from   datalabs.parameter import add_schema, ParameterValidatorMixin
from   datalabs.plugin import import_plugin
from   datalabs import task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


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
    def __init__(self, parameters, data):
        super().__init__(parameters, data)

        self._triggered_tasks = None
        self._status = None

    def run(self):
        dag = self._data[0].decode()
        dag_class = self._extract_dag_class(dag)
        dag_executor = LocalDAGExecutorTask(
            {
                "dag_class": dag_class,
                "task_statuses": self._parameters["task_statuses"]
            }
        )
        LOGGER.info("Running Express DAG %s", dag_class)

        with tempfile.TemporaryDirectory() as python_path:
            self._write_dag(dag_class, dag, python_path)

            sys.path.append(python_path)

            dag_executor.run()

        self._triggered_tasks = dag_executor.triggered_tasks
        self._status = dag_executor.status

    @property
    def triggered_tasks(self):
        return self._triggered_tasks

    @property
    def status(self):
        return self._status

    @classmethod
    def _extract_dag_class(cls, dag):
        lines = dag.split("\n")
        index = 0
        dag_class = None

        while lines[index] == "":
            index += 1

        return re.sub("'|\"| ", "", lines[index])

    @classmethod
    def _write_dag(cls, dag_class, dag, python_path):
        package, module, _ = dag_class.rsplit(".", 2)
        package_path = os.path.join(*package.split("."))
        module_path = os.path.join(package_path, f"{module}.py")

        os.makedirs(os.path.join(python_path, package_path))

        cls._create_packages(python_path, package_path)

        with open(os.path.join(python_path, module_path), "w") as file:
            file.write(dag)

    @classmethod
    def _create_packages(cls, python_path, package_path):
        while package_path:
            init_path = os.path.join(python_path, package_path, "__init__.py")

            with open(init_path, "w"):
                pass

            package_path  = os.path.dirname(package_path)



