""" Support for validating dict parameters via a parameter class with an attached schema. """
import copy

import marshmallow


def add_schema(*args, **kwargs):
    def create_schema(model_class):
        model_fields = [key for key, value in model_class.__dict__.items() if not key.startswith('_')]
        unknown_handling = marshmallow.RAISE

        if '__dataclass_fields__' in model_class.__dict__:
            model_fields = [key for key, value in model_class.__dataclass_fields__.items() if not key.startswith('_')]

        if 'unknowns' in kwargs and kwargs['unknowns']:
            unknown_handling = marshmallow.INCLUDE


        class Schema(marshmallow.Schema):
            class Meta:
                # strict = True
                fields = copy.deepcopy(model_fields)
                unknown = unknown_handling

            @marshmallow.post_load
            #pylint: disable=unused-argument
            def make_model(self, data, **kwargs):
                model = None

                if '__dataclass_fields__' in model_class.__dict__:
                    model = self._make_dataclass_model(data)
                else:
                    model = self._make_class_model(data)

                return model

            def _make_dataclass_model(self, data):
                unknowns = self._extract_unknowns(data)

                self._fill_dataclass_defaults(data)

                if self.Meta.unknown == marshmallow.INCLUDE and 'unknowns' in model_fields and 'unknowns' in data:
                    data['unknowns'] = unknowns

                return model_class(**data)

            def _make_class_model(self, data):
                unknowns = self._extract_unknowns(data)

                self._fill_class_defaults(data)
                model = model_class()

                if self.Meta.unknown == marshmallow.INCLUDE and 'unknowns' in model_fields and 'unknowns' in data:
                    data['unknowns'] = unknowns

                for field in data:
                    setattr(model, field, data[field])

                return model

            def _fill_dataclass_defaults(self, data):
                missing_fields = []

                for field in self.Meta.fields:
                    dataclass_field = model_class.__dict__['__dataclass_fields__'][field]

                    if field not in data and dataclass_field.default.__class__.__name__ != '_MISSING_TYPE':
                        data[field] = dataclass_field.default
                    elif field not in data:
                        missing_fields.append(field)

                if len(missing_fields) > 0:
                    raise ValidationException(
                        f'Missing parameters for {model_class.__name__} instance: {missing_fields}'
                    )

            @classmethod
            def _extract_unknowns(cls, data):
                unknowns = {}
                keys = list(data.keys())

                for key in keys:
                    value = data.pop(key)

                    if key in model_fields:
                        data[key] = value
                    else:
                        unknowns[key] = value

                return unknowns


            def _fill_class_defaults(self, data):
                for field in self.Meta.fields:
                    default = getattr(model_class, field)

                    if field not in data:
                        data[field] = default

        model_class.SCHEMA = Schema()

        return model_class

    return_value = create_schema
    if len(args) == 1:
        return_value = create_schema(args[0])

    return return_value


class ValidationException(Exception):
    pass


class ParameterValidatorMixin:
    @classmethod
    def _get_validated_parameters(cls, parameters: dict):
        parameter_variables = {key.lower():value for key, value in parameters.items()}
        schema = cls.PARAMETER_CLASS.SCHEMA  # pylint: disable=no-member

        return schema.load(parameter_variables)
