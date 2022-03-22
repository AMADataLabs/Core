''' Source: datalabs.etl.dag.awslambda '''
import os

import pytest

from   datalabs.etl.dag.execute.batch import BatchDAGExecutorTask


@pytest.mark.skipif(
    os.getenv('RUN_INTEGRATION_TESTS') != 'True',
    reason="Normally skip integration tests to increase testing speed."
)
# pylint: disable=redefined-outer-name, protected-access, unused-argument
def test_fargate_task_executor(task_runtime_parameters):
    task = BatchDAGExecutorTask(task_runtime_parameters)

    task.run()


@pytest.mark.skipif(
    os.getenv('RUN_INTEGRATION_TESTS') != 'True',
    reason="Normally skip integration tests to increase testing speed."
)
# pylint: disable=redefined-outer-name, protected-access, unused-argument
def test_fargate_dag_executor(dag_runtime_parameters):
    task = BatchDAGExecutorTask(dag_runtime_parameters)

    task.run()


@pytest.fixture
def task_runtime_parameters():
    return dict(
        dag="SOME_DAG",
        job_queue="ecs-scheduler-job-queue",
        job_definition="ecs-scheduler-job-definition",
        execution_time="2021-01-01T00:00:00.000000",
        task="SOME_TASK"
    )


@pytest.fixture
def dag_runtime_parameters():
    return dict(
        dag="SOME_DAG",
        job_queue="ecs-scheduler-job-queue",
        job_definition="ecs-scheduler-job-definition",
        execution_time="2021-01-01T00:00:00.000000"
    )
