""" Support for validating dict parameters via a parameter class with an attached schema. """
import copy

import marshmallow


def add_schema(model_class):
    model_fields = [key for key, value in model_class.__dict__.items() if not key.startswith('_')]

    if '__dataclass_fields__' in model_class.__dict__:
        model_fields = [key for key, value in model_class.__dataclass_fields__.items() if not key.startswith('_')]

    class Schema(marshmallow.Schema):
        class Meta:
            # strict = True
            fields = copy.deepcopy(model_fields)
            unknown = marshmallow.RAISE

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

            if self.Meta.unknown == marshmallow.INCLUDE and 'unknowns' in model_fields and 'unknowns' not in data:
                data['unknowns'] = unknowns

            return model_class(**data)

        def _make_class_model(self, data):
            unknowns = self._extract_unknowns(data)

            self._fill_class_defaults(data)
            model = model_class()

            import pdb; pdb.set_trace()
            if self.Meta.unknown == marshmallow.INCLUDE and 'unknowns' in model_fields:
                setattr(model, 'unknowns', unknowns)

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
                raise ValidationException(f'Missing parameters for {model_class.__name__} instance: {missing_fields}')

        def _extract_unknowns(self, data):
            unknowns = {}

            for key in data.keys():
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


class ValidationException(Exception):
    pass


class ParameterValidatorMixin:
    @classmethod
    def _get_validated_parameters(cls, parameters: dict, unknowns=False):
        parameter_variables = {key.lower():value for key, value in parameters.items()}
        schema = cls.PARAMETER_CLASS.SCHEMA  # pylint: disable=no-member

        if unknowns:
            schema.Meta.unknown = marshmallow.INCLUDE

        return schema.load(parameter_variables)
