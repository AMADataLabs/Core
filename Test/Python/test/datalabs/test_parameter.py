""" source: datalabs.parameter """
from   dataclasses import dataclass
import os

from   marshmallow.exceptions import ValidationError
import pytest

from   datalabs.parameter import add_schema, ParameterValidatorMixin
from   datalabs.task import Task, TaskWrapper


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


# pylint: disable=redefined-outer-name
def test_including_unknown_dataclass_parameters_fills_unknowns_field(model_dataclass_parent):
    class ParameterizedThing(ParameterValidatorMixin):
        PARAMETER_CLASS = model_dataclass_parent

        def __init__(self, parameters):
            self._parameters = self._get_validated_parameters(parameters)

    thing = ParameterizedThing(dict(FOOZIE='stuff', barnacle='bologna', biff='baff', ping='pong'))

    assert thing._parameters.unknowns is not None
    assert 'biff' in thing._parameters.unknowns
    assert 'ping' in thing._parameters.unknowns


# pylint: disable=redefined-outer-name
def test_including_unknown_class_parameters_fills_unknowns_field(model_class_parent):
    class ParameterizedThing(ParameterValidatorMixin):
        PARAMETER_CLASS = model_class_parent

        def __init__(self, parameters):
            self._parameters = self._get_validated_parameters(parameters)

    thing = ParameterizedThing(dict(FOOZIE='stuff', barnacle='bologna', biff='baff', ping='pong'))

    assert thing._parameters.unknowns is not None
    assert 'biff' in thing._parameters.unknowns
    assert 'ping' in thing._parameters.unknowns



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

@pytest.fixture
def model_dataclass_parent():
    @add_schema(unknowns=True)
    @dataclass
    class Model:
        foozie: str
        barnacle: str = 'Bar'
        unknowns: dict = None

    return Model


@pytest.fixture
def model_class_parent():
    @add_schema(unknowns=True)
    class Model:
        foozie = None
        barnacle = 'Bar'
        unknowns = None

    return Model
