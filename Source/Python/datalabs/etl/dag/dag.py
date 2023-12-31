""" Class for defining a DAG. """
from dataclasses import dataclass
import re
from typing import Dict, List, Optional, Type

import paradag

from datalabs.etl.dag.state import Status


class DAGTask:
    def __init__(self, task_id: str, task_class: type):
        self._id = task_id
        self._task_class = task_class
        self._successors: List[DAGTask] = []
        self._predecessors: List[DAGTask] = []
        self._dag: Optional[DAG] = None
        self._ready: Optional[bool] = True
        self._status: Optional[Status] = Status.UNKNOWN

    def __repr__(self):
        return f"DAGTask('{self.id}', {self._task_class})"

    def __str__(self):
        return self.id

    def set_dag(self, dag: "DAG"):
        self._dag = dag

    def set_status(self, status: Status):
        self._status = status

    @property
    # pylint: disable=redefined-outer-name, invalid-name
    def id(self):
        return self._id

    @property
    def successors(self):
        return self._successors

    @property
    def predecessors(self):
        return self._predecessors

    @property
    def ready(self):
        return self._ready

    @property
    def task_class(self):
        return self._task_class

    @property
    def status(self):
        return self._status

    def __rshift__(self, other: "DAGTask"):
        self._successors.append(other)
        other._predecessors.append(self)

        return other

    def block(self):
        self._ready = False

    def unblock(self):
        self._ready = True


class DAGMeta(type):
    # pylint: disable=bad-mcs-classmethod-argument
    def __new__(mcs, classname, bases, attrs, **kwargs):
        cls = super().__new__(mcs, classname, bases, attrs, **kwargs)
        cls.__task_classes__ = {}

        if hasattr(cls, "__annotations__"):
            for task, task_annotation in cls.__annotations__.items():
                cls._generate_task(task, task_annotation)

        return cls

    def __getattr__(cls, name):
        if name not in cls.__task_classes__:
            raise AttributeError(f"type object '{cls.__name__}' has no attribute '{name}'")

        return cls.__task_classes__.get(name)

    @property
    def tasks(cls):
        return cls.__task_classes__.keys()

    def _generate_task(cls, task, task_annotation):
        if type(task_annotation).__name__ == "Repeat":
            # pylint: disable=no-value-for-parameter
            cls._generate_subtasks(task, task_annotation)
        else:
            cls.__task_classes__[task] = DAGTask(task, task_annotation)

    def _generate_subtasks(cls, task, repeat):
        for index in range(repeat.start, repeat.count):
            cls.__task_classes__[f"{task}_{index}"] = DAGTask(f"{task}_{index}", repeat.task_class)


class DAG(paradag.DAG, metaclass=DAGMeta):
    CLASSES: Dict[str, Type] = {}

    def __init__(self):
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

    @property
    def graph(self):
        lines = ["digraph {"]

        for task in self.vertices():
            for successor in task.successors:
                lines.append(f"    {task.id} -> {successor.id}")

        lines.append("}")

        return "\n".join(lines)

    @classmethod
    def task_class(cls, task: str):
        dag_task = cls.__task_classes__.get(task)

        if dag_task is None:
            raise ValueError(f"DAG {cls.__name__} has no task {task}.")

        return dag_task.task_class

    @classmethod
    def downstream_tasks(cls, task: str):
        dag_task = cls.__task_classes__.get(task)
        downstream_tasks = []

        if dag_task is None:
            raise ValueError(f"DAG {cls.__name__} has no task {task}")

        for successor in dag_task.successors:
            downstream_tasks.append(successor.id)
            downstream_tasks += cls.downstream_tasks(successor.id)

        return set(downstream_tasks)

    @classmethod
    def upstream_tasks(cls, task: str):
        dag_task = cls.__task_classes__.get(task)
        upstream_tasks = []

        if dag_task is None:
            raise ValueError(f"DAG {cls.__name__} has no task {task}")

        for predecessor in dag_task.predecessors:
            upstream_tasks.append(predecessor.id)
            upstream_tasks += cls.upstream_tasks(predecessor.id)

        return set(upstream_tasks)

    @classmethod
    def sequence(cls, task, start=None, count=None):
        if start is None:
            start = 0

        if count is None:
            count = len(cls._subtasks(task))
        for index in range(start + 1, count):
            # pylint: disable=expression-not-assigned
            getattr(cls, f"{task}_{index-1}") >> getattr(cls, f"{task}_{index}")

    @classmethod
    def parallel(cls, task1, task2, start=None, count=None):
        if start is None:
            start = 0

        if count is None:
            count = len(cls._subtasks(task1))

        for index in range(start, count):
            # pylint: disable=expression-not-assigned
            getattr(cls, f"{task1}_{index}") >> getattr(cls, f"{task2}_{index}")

    @classmethod
    def fan_in(cls, task1, task2, start=None, count=None):
        if start is None:
            start = 0

        if count is None:
            count = len(cls._subtasks(task1))

        for index in range(start, count):
            # pylint: disable=expression-not-assigned
            getattr(cls, f"{task1}_{index}") >> getattr(cls, task2)

    @classmethod
    def fan_out(cls, task1, task2, start=None, count=None):
        if start is None:
            start = 0

        if count is None:
            count = len(cls._subtasks(task2))

        for index in range(start, count):
            # pylint: disable=expression-not-assigned
            getattr(cls, f"{task1}") >> getattr(cls, f"{task2}_{index}")

    @classmethod
    def first(cls, task: str):
        subtasks = cls._subtasks(task)

        if len(subtasks) == 0:
            raise ValueError(f"DAG {cls.__name__} has no subtasks with base name {task}")

        return subtasks[0]

    @classmethod
    def last(cls, task: str):
        subtasks = cls._subtasks(task)

        if len(subtasks) == 0:
            raise ValueError(f"DAG {cls.__name__} has no subtasks with base name {task}")

        return subtasks[-1]

    @classmethod
    def _subtasks(cls, task: str):
        regex = re.compile(f"{task}_[0-9]+")
        subtasks = sorted(key for key in cls.__task_classes__.keys() if regex.match(key))

        return [getattr(cls, key) for key in subtasks]


def register(*args, **kwargs):
    def register_class(dag_class):
        if "name" in kwargs:
            DAG.CLASSES[kwargs["name"]] = dag_class

        return dag_class

    return_value = register_class

    if len(args) == 1:
        return_value = register_class(args[0])

    return return_value


@dataclass
class Repeat:
    task_class: type
    count: int
    start: int = 0
