''' Source: datalabs.etl.dag.aws '''
import logging
import os
import tempfile

import mock

import pytest

from   datalabs.etl.dag import DAG
from   datalabs.etl.dag.aws import DAGTaskWrapper

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=redefined-outer-name, protected-access, unused-argument
def test_runtime_parameters_are_combined(args, environment, dag_parameters, expected_runtime_parameters):
    with mock.patch.object(DAGTaskWrapper, '_get_dag_task_parameters_from_dynamodb') \
            as _get_dag_task_parameters_from_dynamodb:
        _get_dag_task_parameters_from_dynamodb.return_value = dag_parameters
        task_wrapper = DAGTaskWrapper(args)

        runtime_parameters = task_wrapper._get_runtime_parameters(task_wrapper._parameters)

        assert runtime_parameters == expected_runtime_parameters


# pylint: disable=redefined-outer-name, protected-access, unused-argument
def test_task_parameters_override_runtime_parameters(args, environment, get_dag_task_parameters_from_dynamodb):
    task_wrapper = DAGTaskWrapper(args)

    with mock.patch.object(DAGTaskWrapper, '_get_dag_task_parameters_from_dynamodb') \
            as _get_dag_task_parameters_from_dynamodb:
        with mock.patch.object(DAGTaskWrapper, '_notify_dag'):
            _get_dag_task_parameters_from_dynamodb.side_effect = get_dag_task_parameters_from_dynamodb

            task_wrapper.run()

    LOGGER.debug("Runtime Parameters: %s", task_wrapper._runtime_parameters)

    assert len(task_wrapper._task_parameters) == 3
    assert task_wrapper._runtime_parameters["LAMBDA_FUNCTION"] == 'MyAppStack-sbx-MyBigTask'
    assert task_wrapper._runtime_parameters["TASK_EXECUTOR_CLASS"] == 'com.dancinglamb.LambdaTaskExecutorTask'


# pylint: disable=redefined-outer-name, protected-access, unused-argument
def test_dynamic_parameter_substitutions(args_parameters, environment, dag_parameters, task_parameters):
    task_parameters["CORNBREAD_TEMPERATURE"] = "3${PARAMETER_SET_INDEX}"
    task_parameters["BASE_METRIC"] = "${ALGORITHM_NAME}Standard"

    with mock.patch.object(DAGTaskWrapper, '_get_dag_task_parameters_from_dynamodb') \
            as _get_dag_task_parameters_from_dynamodb:
        _get_dag_task_parameters_from_dynamodb.return_value = dag_parameters
        task_wrapper = DAGTaskWrapper(args_parameters)
        task_wrapper._runtime_parameters = task_wrapper._get_runtime_parameters(task_wrapper._parameters)
        _get_dag_task_parameters_from_dynamodb.return_value = task_parameters

        task_parameters = task_wrapper._get_dag_task_parameters()

        assert task_parameters["CORNBREAD_TEMPERATURE"] == '35'
        assert task_parameters["BASE_METRIC"] == 'SuperAwesomeStandard'


@pytest.fixture
def args():
    return ['task.py', '{"dag": "MY_DAG", "type": "Task", "task": "MY_TASK", "execution_time": "2022-03-26T00:00:00"}']


@pytest.fixture
def args_parameters():
    return [
        'task.py',
        '{"dag": "MY_DAG", "type": "Task", "task": "MY_TASK", "execution_time": "2022-03-26T00:00:00", '\
        '"parameters": {"ALGORITHM_NAME": "SuperAwesome", "PARAMETER_SET_INDEX": 5}}'
    ]


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
def state_directory():
    with tempfile.TemporaryDirectory() as directory:
        yield directory


@pytest.fixture
def dag_parameters(state_directory):
    return dict(
        LAMBDA_FUNCTION='MyAppStack-sbx-MyETL',
        DAG_CLASS='test.datalabs.etl.dag.test_aws.MyDAG',
        DAG_STATE_PARAMETERS=f'''
            {{
                "DAG_STATE_CLASS": "datalabs.etl.dag.state.file.DAGState",
                "BASE_PATH": "{state_directory}"
            }}
        ''',
        DAG_TOPIC_ARN='arn:aws:sns:us-east-1:644454719059:DataLake-sbx-DAGProcessor',
        TASK_TOPIC_ARN='arn:aws:sns:us-east-1:644454719059:DataLake-sbx-TaskProcessor',
        DAG_EXECUTOR_CLASS='datalabs.etl.dag.execute.awslambda.LambdaDAGExecutorTask',
        TASK_EXECUTOR_CLASS='datalabs.etl.dag.execute.awslambda.LambdaTaskExecutorTask'
    )


@pytest.fixture
def task_parameters():
    return dict(
        OVERRIDES='''
            {
                "LAMBDA_FUNCTION": "MyAppStack-sbx-MyBigTask",
                "TASK_EXECUTOR_CLASS": "com.dancinglamb.LambdaTaskExecutorTask"
            }
        ''',
        TASK_CLASS="datalabs.etl.task.DummyTask",
        CORNBREAD_TEMPERATURE='32',
        BASE_METRIC='grit'
    )


@pytest.fixture
def expected_runtime_parameters(state_directory):
    return dict(
        LAMBDA_FUNCTION='MyAppStack-sbx-MyETL',
        DAG_CLASS='test.datalabs.etl.dag.test_aws.DAG',
        DAG_STATE_PARAMETERS=f'''
            {{
                "DAG_STATE_CLASS": "datalabs.etl.dag.state.file.DAGState",
                "BASE_PATH": "{state_directory}"
            }}
        ''',
        DAG_TOPIC_ARN='arn:aws:sns:us-east-1:644454719059:DataLake-sbx-DAGProcessor',
        TASK_TOPIC_ARN='arn:aws:sns:us-east-1:644454719059:DataLake-sbx-TaskProcessor',
        DAG_EXECUTOR_CLASS='datalabs.etl.dag.execute.awslambda.LambdaDAGExecutorTask',
        TASK_EXECUTOR_CLASS='datalabs.etl.dag.execute.awslambda.LambdaTaskExecutorTask',
        dag='MY_DAG',
        type='Task',
        task='MY_TASK',
        execution_time='2022-03-26T00:00:00'
    )

@pytest.fixture
def get_dag_task_parameters_from_dynamodb(dag_parameters, task_parameters):
    def _get_dag_task_parameters_from_dynamodb(dag, task):
        parameters = task_parameters

        if task == "DAG":
            parameters = dag_parameters

        return parameters

    return _get_dag_task_parameters_from_dynamodb


class MyDAG(DAG):
    MY_TASK: "datalabs.etl.transform.PassThroughTransformerTask"
