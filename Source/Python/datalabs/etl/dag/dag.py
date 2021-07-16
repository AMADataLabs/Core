""" Class for defining a DAG. """
import paradag


class DAGTask:
    def __init__(self, task_id: str, task_class: str):
        self._id = task_id
        self._task_class = task_class
        self._successors = []
        self._dag = None
        self._ready = True

    def __str__(self):
        return self.id

    def set_dag(self, dag: 'DAG'):
        self._dag = dag

    @property
    # pylint: disable=redefined-outer-name, invalid-name
    def id(self):
        return self._id

    @property
    def successors(self):
        return self._successors

    @property
    def ready(self):
        return self._ready

    @property
    def task_class(self):
        return self._task_class

    def __rshift__(self, other: 'DAGTask'):
        self._successors.append(other)

        return other

    def block(self):
        self._ready = False


class DAGMeta(type):
    # pylint: disable=bad-mcs-classmethod-argument
    def __new__(mcs, classname, bases, attrs, **kwargs):
        cls = super().__new__(mcs, classname, bases, attrs, **kwargs)
        cls.__task_classes__ = {}

        if hasattr(cls, '__annotations__'):
            for task, task_class in cls.__annotations__.items():
                cls.__task_classes__[task] = DAGTask(task, task_class)

        return cls

    def __getattr__(cls, name):
        if name not in cls.__task_classes__:
            raise AttributeError(f"type object '{cls.__name__}' has no attribute '{name}'")

        return cls.__task_classes__.get(name)


class DAG(paradag.DAG, metaclass=DAGMeta):
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

    @classmethod
    def task_class(cls, task: str):
        return cls.__task_classes__.get(task).task_class
