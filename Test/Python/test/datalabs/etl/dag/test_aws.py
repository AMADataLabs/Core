''' Source: datalabs.etl.dag.aws '''
import os

import mock

import pytest

from   datalabs.etl.dag.aws import DAGTaskWrapper


# pylint: disable=redefined-outer-name, protected-access, unused-argument
def test_runtime_parameters_are_combined(args, environment, dag_parameters, expected_runtime_parameters):
    with mock.patch.object(DAGTaskWrapper, '_get_dag_task_parameters_from_dynamodb') \
            as _get_dag_task_parameters_from_dynamodb:
        _get_dag_task_parameters_from_dynamodb.return_value = dag_parameters
        task_wrapper = DAGTaskWrapper(parameters=args)

        runtime_parameters = task_wrapper._get_runtime_parameters(task_wrapper._parameters)

        assert runtime_parameters == expected_runtime_parameters


# pylint: disable=redefined-outer-name, protected-access, unused-argument
def test_task_parameters_override_runtime_parameters(args, environment, dag_parameters, task_parameters):
    with mock.patch.object(DAGTaskWrapper, '_get_dag_task_parameters_from_dynamodb') \
            as _get_dag_task_parameters_from_dynamodb:
        _get_dag_task_parameters_from_dynamodb.return_value = dag_parameters
        task_wrapper = DAGTaskWrapper(parameters=args)
        task_wrapper._runtime_parameters = task_wrapper._get_runtime_parameters(task_wrapper._parameters)
        _get_dag_task_parameters_from_dynamodb.return_value = task_parameters

        task_parameters = task_wrapper._get_dag_task_parameters()

        assert len(task_parameters) == 2
        assert task_wrapper._runtime_parameters["LAMBDA_FUNCTION"] == 'MyAppStack-sbx-MyBigTask'
        assert task_wrapper._runtime_parameters["TASK_EXECUTOR_CLASS"] == 'com.dancinglamb.LambdaTaskExecutorTask'


@pytest.fixture
def args():
    return ['task.py', 'MY_DAG__MY_TASK__2022-03-26T00:00:00']


@pytest.fixture
def environment():
    current_env = os.environ.copy()

    os.environ['TASK_WRAPPER_CLASS'] = 'datalabs.etl.dag.aws.DAGTaskWrapper'
    os.environ['TASK_RESOLVER_CLASS'] = 'datalabs.etl.dag.resolve.TaskResolver'
    os.environ['DYNAMODB_CONFIG_TABLE'] = 'DataLake-configuration-sbx'

    yield os.environ

    os.environ.clear()
    os.environ.update(current_env)


@pytest.fixture
def dag_parameters():
    return dict(
        LAMBDA_FUNCTION='MyAppStack-sbx-MyETL',
        DAG_CLASS='datalabs.etl.dag.cpt.api.MY_DAGDAG',
        DAG_STATE_CLASS='datalabs.etl.dag.state.dynamodb.DAGState',
        DAG_STATE_TABLE='DataLake-dag-state-sbx',
        STATE_LOCK_TABLE='DataLake-scheduler-locks-sbx',
        DAG_TOPIC_ARN='arn:aws:sns:us-east-1:644454719059:DataLake-sbx-DAGProcessor',
        TASK_TOPIC_ARN='arn:aws:sns:us-east-1:644454719059:DataLake-sbx-TaskProcessor',
        DAG_EXECUTOR_CLASS='datalabs.etl.dag.execute.awslambda.LambdaDAGExecutorTask',
        TASK_EXECUTOR_CLASS='datalabs.etl.dag.execute.awslambda.LambdaTaskExecutorTask'
    )


@pytest.fixture
def task_parameters():
    return dict(
        LAMBDA_FUNCTION='MyAppStack-sbx-MyBigTask',
        TASK_EXECUTOR_CLASS='com.dancinglamb.LambdaTaskExecutorTask',
        CORNBREAD_TEMPERATURE='32',
        BASE_METRIC='grit'
    )


@pytest.fixture
def expected_runtime_parameters():
    return dict(
        LAMBDA_FUNCTION='MyAppStack-sbx-MyETL',
        DAG_CLASS='datalabs.etl.dag.cpt.api.MY_DAGDAG',
        DAG_STATE_CLASS='datalabs.etl.dag.state.dynamodb.DAGState',
        DAG_STATE_TABLE='DataLake-dag-state-sbx',
        STATE_LOCK_TABLE='DataLake-scheduler-locks-sbx',
        DAG_TOPIC_ARN='arn:aws:sns:us-east-1:644454719059:DataLake-sbx-DAGProcessor',
        TASK_TOPIC_ARN='arn:aws:sns:us-east-1:644454719059:DataLake-sbx-TaskProcessor',
        DAG_EXECUTOR_CLASS='datalabs.etl.dag.execute.awslambda.LambdaDAGExecutorTask',
        TASK_EXECUTOR_CLASS='datalabs.etl.dag.execute.awslambda.LambdaTaskExecutorTask',
        dag='MY_DAG',
        task='MY_TASK',
        execution_time='2022-03-26T00:00:00'
    )
