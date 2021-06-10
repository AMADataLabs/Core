""" Class for defining a DAG. """
from   dataclasses import dataclass

import paradag

from   datalabs.etl.dag.state import State
from   datalabs.parameter import add_schema, ParameterValidatorMixin


class DAGTask:
    def __init__(self, dag_class: 'DAG', task_class: str):
        self._dag = dag_class
        self._task_class = task_class
        self._ready = True

    @property
    def task_class(self):
        return self._task_class

    def __rshift__(self, other: 'DAGTask'):
        self._dag.add_edge(self, other)

        return other

    def block(self):
        self._ready = False


class DAGMeta(type):
    def __new__(mcs, classname, bases, attrs, **kwargs):
        cls = super().__new__(mcs, classname, bases, attrs, **kwargs)
        cls.__task_classes__ = {}

        if hasattr(cls, '__annotations__'):
            for task, task_class in cls.__annotations__.items():
                cls.__task_classes__[task] = DAGTask(cls, task_class)

        return cls

    def __getattr__(cls, name):
        if name not in cls.__task_classes__:
            raise AttributeError(f"type object '{cls.__name__}' has no attribute '{name}'")

        return cls.__task_classes__.get(name)

    # TODO: allow DAG.TASK1 >> DAG.TASK2


@dataclass
class DAGParameters:
    state_class: str


class DAG(ParameterValidatorMixin, paradag.DAG, metaclass=DAGMeta):
    PARAMETER_CLASS = DAGParameters

    def __init__(self, parameters: DAGParameters):
        super().__init__()
        self._parameters = self._get_validated_parameters(parameters)

    @classmethod
    def task_class(cls, task: str):
        return cls.__task_classes__.get(task).task_class

    def run(self):
        paradag.dag_run(dag, processor=paradag.MultiThreadProcessor(), executor=DAGExecutor())


class DAGExecutor:
    def __init__(self, dag: DAG):
        self._dag = dag

    def param(self, task: DAGTask):
        return task

    def execute(self, task):
        state = self._get_task_state(task)

        if state == State.UNKNOWN:
            self._trigger_task(task)

        return state

    def deliver(self, task, predecessor_result):
        if predecessor_result != State.FINISHED:
            task.block()

    def _get_task_state(self, task):
        pass

    def _trigger_task(self, task):
        pass
