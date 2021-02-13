""" source: datalabs.task """
from   dataclasses import dataclass

from   marshmallow.exceptions import ValidationError
import pytest

from   datalabs.task import Task, TaskWrapper, add_schema

def test_task_is_abstract():
    with pytest.raises(TypeError):
        BadTask(None)  # pylint: disable=abstract-class-instantiated


def test_task_is_not_abstract():
    GoodTask(None).run()


def test_task_wrapper_is_abstract():
    with pytest.raises(TypeError):
        BadTaskWrapper(None)  # pylint: disable=abstract-class-instantiated


def test_task_wrapper_is_not_abstract():
    GoodTaskWrapper(GoodTask).run()


def test_task_lineage_is_bad():
    with pytest.raises(TypeError):
        GoodTaskWrapper('Task Class')


# pylint: disable=redefined-outer-name
def test_adding_schema_to_dataclass_yields_correct_schema_fields(model_dataclass):
    assert hasattr(model_dataclass, 'SCHEMA')
    assert hasattr(model_dataclass.SCHEMA, 'fields')
    assert len(model_dataclass.SCHEMA.Meta.fields) == 2
    assert 'foozie' in model_dataclass.SCHEMA.Meta.fields
    assert 'barnacle' in model_dataclass.SCHEMA.Meta.fields


# pylint: disable=redefined-outer-name
def test_adding_schema_to_dataclass_yields_correct_schema_field_defaults(model_dataclass):
    model = model_dataclass.SCHEMA.load(dict(foozie='Foo'))

    assert model.foozie == 'Foo'
    assert model.barnacle == 'Bar'


# pylint: disable=redefined-outer-name
def test_deserializing_dataclass_with_none_parameter_yields_deserialization_error(model_dataclass):
    with pytest.raises(ValidationError):
        model_dataclass.SCHEMA.load(dict(foozie=None))



def test_deserializing_dataclass_with_none_default_is_ok():
    @add_schema
    @dataclass
    class Model:
        foozie: str = None
        barnacle: str = 'Bar'

    model = Model.SCHEMA.load(dict())  # pylint: disable=no-member

    assert model.foozie is None


# pylint: disable=redefined-outer-name
def test_adding_schema_to_class_yields_correct_schema_fields(model_class):
    assert hasattr(model_class, 'SCHEMA')
    assert hasattr(model_class.SCHEMA, 'fields')
    assert len(model_class.SCHEMA.Meta.fields) == 2
    assert 'foozie' in model_class.SCHEMA.Meta.fields
    assert 'barnacle' in model_class.SCHEMA.Meta.fields


# pylint: disable=redefined-outer-name
def test_adding_schema_to_class_yields_correct_schema_field_defaults(model_class):
    model = model_class.SCHEMA.load(dict(foozie='Foo'))

    assert model.foozie == 'Foo'
    assert model.barnacle == 'Bar'


# pylint: disable=abstract-method
class BadTask(Task):
    pass


class GoodTask(Task):
    def run(self):
        pass


class BadTaskWrapper(TaskWrapper):
    pass


class GoodTaskWrapper(TaskWrapper):
    def _get_task_parameters(self):
        pass

    def _handle_success(self) -> (int, dict):
        pass

    def _handle_exception(self, exception: Exception) -> (int, dict):
        pass


@pytest.fixture
def model_dataclass():
    @add_schema
    @dataclass
    class Model:
        foozie: str
        barnacle: str = 'Bar'

    return Model


@pytest.fixture
def model_class():
    @add_schema
    class Model:
        foozie = None
        barnacle = 'Bar'

    return Model
