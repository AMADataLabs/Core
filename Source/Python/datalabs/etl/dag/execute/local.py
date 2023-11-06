''' Classes for executing DAGs and DAG tasks locally. '''
from   collections import Counter
from   dataclasses import dataclass
import logging

import paradag

from   datalabs.etl.dag.state import Status
from   datalabs.parameter import add_schema
from   datalabs.plugin import import_plugin
from   datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@add_schema
@dataclass
class LocalDAGExecutorParameters:
    dag_class: str
    task_statuses: dict


class LocalDAGExecutorTask(Task):
    """ DAG objects are defined in DAG modules where their vertexes (tasks) and edges are defined. An instance of the
        DAG is instantiated dynamically by the provided class name.
    """
    PARAMETER_CLASS = LocalDAGExecutorParameters

    def __init__(self, parameters: dict, data: "list<bytes>"=None):
        super().__init__(parameters, data)

        self._triggered_tasks = []
        self._status = Status.PENDING

    def run(self):
        dag = import_plugin(self._parameters.dag_class)()

        for _, task in dag.__task_classes__.items():
            LOGGER.debug('Initially unblocking task "%s"', task.id)
            task.unblock()

        tasks = paradag.dag_run(
            dag,
            processor=paradag.MultiThreadProcessor(),
            # processor=paradag.SequentialProcessor(),
            executor=self
        )

        self._set_dag_status_from_task_statuses([task.status for task in tasks])

    @property
    def triggered_tasks(self):
        return self._triggered_tasks

    @property
    def status(self):
        return self._status

    # pylint: disable=no-self-use
    def param(self, task: 'DAGTask'):
        """ This paradag method is used by paradag to allow for a set of vertex-derived parameters to be used in
            execution of a DAG vertex. In our case, as is often done, we just return the vertex (task) object itself and
            operate on it directly during execution.
        """
        return task

    # pylint: disable=assignment-from-no-return
    def execute(self, task):
        """ This paradag method executes the given DAG vertex (task). """
        status = self._get_task_status(task)
        LOGGER.info('Task "%s" is ready? %s', task.id, task.ready)

        if status in [Status.UNKNOWN, Status.PAUSED] and task.ready:
            self._trigger_task(task)

        return status

    # pylint: disable=no-self-use
    def deliver(self, task, predecessor_result):
        """ This paradag method is called after executing a vertex (task) and before executing the given successor
            vertex (i.e. deliver the results of a vertex to its successor vertices). We use the method to determine
            whether the given task is ready to run based on all its predecessor tasks' execution statuses. If any
            predecessor task has not finished, the given task is blocked from running.
        """
        LOGGER.debug('Result of predecessor to task "%s": %s', task.id, predecessor_result)

        if predecessor_result != Status.FINISHED:
            LOGGER.debug('Blocking task "%s"', task.id)
            task.block()

    def _set_dag_status_from_task_statuses(self, task_statuses):
        task_status_counts = Counter(task_statuses)

        if task_status_counts[Status.FINISHED] == len(task_statuses):
            self._status = Status.FINISHED
        elif task_status_counts[Status.FAILED] > 0:
            self._status = Status.FAILED
        elif (task_status_counts[Status.FAILED]) == 0:
            self._status = Status.RUNNING

        LOGGER.info('Set status of DAG to "%s"', self._status)

    def _get_task_status(self, task):
        status = self._parameters.task_statuses.get(task.id, Status.UNKNOWN)

        task.set_status(status)

        LOGGER.info('State of task "%s": %s', task.id, status)

        return status

    def _trigger_task(self, task):
        LOGGER.info('Triggering task "%s"', task.id)
        LOGGER.debug('Triggered tasks: %s', self._triggered_tasks)
        self._triggered_tasks.append(task.id)
