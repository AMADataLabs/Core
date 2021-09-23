""" source: datalabs.etl.transform """
import pytest

from datalabs.etl.transform import TransformerTask, PassThroughTransformerTask


# pylint: disable=redefined-outer-name
def test_transformer_task(transformer):
    transformer.run()

    assert transformer.data == 'True'


def test_pass_through_transformer():
    transformer = PassThroughTransformerTask(dict(data='True'))

    transformer.run()


    assert transformer.data


@pytest.fixture
def transformer():
    return Transformer(dict(data='True'))


class Transformer(TransformerTask):
    def _transform(self):
        return str(self._parameters['data'])
