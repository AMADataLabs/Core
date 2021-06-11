""" Class for defining a DAG. """
from   collections import defaultdict
from   dataclasses import dataclass

import paradag

from   datalabs.etl.dag.state import State
from   datalabs.parameter import add_schema, ParameterValidatorMixin


class DAGTask:
    def __init__(self, task_class: str):
        self._task_class = task_class
        self._successors = []
        self._dag = None
        self._ready = True

    def set_dag(self, dag: 'DAG'):
        self._dag = dag

    @property
    def successors(self):
        return self._successors

    @property
    def task_class(self):
        return self._task_class

    def __rshift__(self, other: 'DAGTask'):
        self._successors.append(other)

        return other

    def block(self):
        self._ready = False


class DAGMeta(type):
    def __new__(mcs, classname, bases, attrs, **kwargs):
        cls = super().__new__(mcs, classname, bases, attrs, **kwargs)
        cls.__task_classes__ = {}

        if hasattr(cls, '__annotations__'):
            for task, task_class in cls.__annotations__.items():
                cls.__task_classes__[task] = DAGTask(task_class)

        return cls

    def __getattr__(cls, name):
        if name not in cls.__task_classes__:
            raise AttributeError(f"type object '{cls.__name__}' has no attribute '{name}'")

        return cls.__task_classes__.get(name)


class DAG(paradag.DAG, metaclass=DAGMeta):
    def __init__(self, state_class):
        super().__init__()

        for task in self.__task_classes__.values():
            task.set_dag(self)
            self.add_vertex(task)

        for task in self.__task_classes__.values():
            for successor in task.successors:
                self.add_edge(task, successor)

    def __getattr__(self, name):
        if name not in self.__task_classes__:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

        return self.__task_classes__.get(name)

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
