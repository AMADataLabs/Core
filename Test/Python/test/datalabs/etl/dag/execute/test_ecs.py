''' Source: datalabs.etl.dag.awslambda '''
import os

import pytest

from   datalabs.etl.dag.execute.ecs import FargateDAGExecutorTask


@pytest.mark.skipif(
    os.getenv('RUN_INTEGRATION_TESTS') != 'True',
    reason="Normally skip integration tests to increase testing speed."
)
# pylint: disable=redefined-outer-name, protected-access, unused-argument
def test_dag_processor_runs():
    os.environ['TASK_CLASS'] = 'datalabs.etl.dag.process.DAGProcessorTask'
    os.environ['DAG_CLASS'] = 'datalabs.etl.dag.schedule.dag.DAGSchedulerDAG'

    wrapper = FargateDAGExecutorTask()

    wrapper.run()


@pytest.fixture
def runtime_parameters():
    return dict(
        dag="SOME_DAG",
        job="SOME_JOB",
        task="SOME_TASK",
        execution_time="2021-01-01T00:00:00.000000"
    )
