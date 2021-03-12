""" source: datalabs.etl.cpt.router """
import os
import pytest

from   datalabs.etl.cpt.router import RouterTaskWrapper, RouterTask


# pylint: disable=redefined-outer-name, protected-access, unused-argument
def test_router_variables_are_parsed(environment_variables):
    task_wrapper = RouterTaskWrapper(task_class=DummyClass)
    task_parameters = task_wrapper._get_task_parameters()

    assert 'ACCOUNT' in task_parameters
    assert 'BASE_PATH' in task_parameters
    assert 'FUNCTIONS' in task_parameters
    assert 'REGION' in task_parameters


# pylint: disable=redefined-outer-name, protected-access, unused-argument
def test_router_router_task_using_correct_base_path(environment_variables):
    task_wrapper = RouterTaskWrapper(task_class=RouterTask)
    task_parameters = task_wrapper._get_task_parameters()
    task = RouterTask(task_parameters)

    assert task._parameters.base_path == "AMA/CPT"


class DummyClass:
    def run(self):
        pass


@pytest.fixture
def task_parameters():
    return dict(
        ROUTER__ACCOUNT="644454719059",
        ROUTER__BASE_PATH="AMA/CPT",
        ROUTER__FUNCTIONS="CPTConvert,CPTBundlePDF",
        ROUTER__REGION="us-east-1",
        TASK_CLASS="datalabs.etl.cpt.router.RouterTask",
        TASK_WRAPPER_CLASS="datalabs.etl.cpt.router.RouterTaskWrapper"
    )


@pytest.fixture
def environment_variables(task_parameters):
    current_env = os.environ.copy()

    os.environ.update(task_parameters)

    yield os.environ

    os.environ.clear()
    os.environ.update(current_env)
