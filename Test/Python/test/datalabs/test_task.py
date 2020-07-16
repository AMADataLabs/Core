""" REPLACE WITH DOCSTRING """
import pytest

from datalabs.task import Task


class BadTask(Task):
    pass


class GoodTask(Task):
    def run(self):
        pass


def test_task_is_abstract():
    with pytest.raises(TypeError):
        BadTask(None)


def test_task_is_not_abstract():
    GoodTask(None).run()
