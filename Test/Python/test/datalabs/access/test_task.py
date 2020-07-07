import pytest

import mock

from datalabs.access.task import APIEndpointTask, APIEndpointParameters


class BadTask(APIEndpointTask):
    pass


class GoodTask(APIEndpointTask):
    def _run(self, session):
        GoodTask._run.called = True

GoodTask._run.called = False


def test_task_is_abstract():
    with pytest.raises(TypeError):
        BadTask(None)


def test_task_is_not_abstract():
    GoodTask(None)._run(None)


def test_task_runs_with_database():
    with mock.patch('datalabs.access.task.Database') as database:
        database.return_value.session = True
        parameters = APIEndpointParameters(
            path=None,
            query=None,
            database=dict(name=None, backend=None, host=None, username=None, password=None)
        )
        task = GoodTask(parameters)
        task.run()

        assert database.call_count == 1
        assert database.return_value.session == True
        assert GoodTask._run.called == True
