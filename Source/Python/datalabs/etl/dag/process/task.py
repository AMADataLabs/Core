''' DAG and Task Processor component classes. '''
from   dataclasses import dataclass
import logging

from   datalabs.etl.dag.state import StatefulDAGMixin
from   datalabs.etl.dag.state import Status
from   datalabs.etl.dag.plugin import PluginExecutorMixin
from   datalabs.parameter import add_schema
from   datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@add_schema(unknowns=True)
@dataclass
class DAGProcessorParameters:
    dag: str
    execution_time: str
    dag_class: str
    dag_state: dict
    dag_executor_class: str
    unknowns: dict=None


class DAGProcessorTask(StatefulDAGMixin, PluginExecutorMixin, Task):
    PARAMETER_CLASS = DAGProcessorParameters

    def run(self):
        LOGGER.debug('DAG Processor Parameters: %s', self._parameters)
        state = self._get_state_plugin(self._parameters)
        executor = self._get_plugin(self._parameters.dag_executor_class, self._parameters)

        status = state.get_dag_status(self._parameters.dag, self._parameters.execution_time)
        LOGGER.info('DAG %s Status: %s', self._parameters.dag, status.value)

        if status == Status.UNKNOWN:
            LOGGER.info('Setting DAG %s status to %s', self._parameters.dag, Status.PENDING)
            success = state.set_dag_status(self._parameters.dag, self._parameters.execution_time, Status.PENDING)

            if not success:
                LOGGER.warning('Unable to set DAG %s status', self._parameters.dag)

        executor.run()


@add_schema(unknowns=True)
@dataclass
class TaskProcessorParameters:
    dag: str
    task: str
    execution_time: str
    dag_class: str
    dag_state: dict
    task_executor_class: str
    unknowns: dict=None


class TaskProcessorTask(StatefulDAGMixin, PluginExecutorMixin, Task):
    PARAMETER_CLASS = TaskProcessorParameters

    # pylint: disable=too-many-statements
    def run(self):
        LOGGER.debug('Task Processor Parameters: %s', self._parameters)
        dag = self._parameters.dag
        task = self._parameters.task
        execution_time = self._parameters.execution_time
        state = self._get_state_plugin(self._parameters)
        executor = self._get_plugin(self._parameters.task_executor_class, self._parameters)

        status = state.get_task_status(dag, task, execution_time)
        LOGGER.info('Task %s Status for DAG %s: %s', task, dag, status.value)

        if status != Status.UNKNOWN:
            raise ValueError(f'Task {task} for DAG {dag} has already been run for execution time {execution_time}')

        set_succeeded = state.set_task_status(dag, task, execution_time, Status.PENDING)

        if not set_succeeded:
            raise ValueError(f'Task {task} for DAG {dag} has already been run for execution time {execution_time}')

        LOGGER.info('Running task %s of dag %s...', task, dag)
        executor.run()
