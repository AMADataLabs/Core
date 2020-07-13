import pytest

from datalabs.etl.transform import TransformerTask, PassThroughTransformerTask


def test_transformer_task(transformer):
    transformer.run()

    assert transformer.data == 'True'


def test_pass_through_transformer():
    transformer = PassThroughTransformerTask(dict(data=True))

    transformer.run()


    assert transformer.data == True


@pytest.fixture
def transformer():
    class Transformer(TransformerTask):
        def _transform(self, data):
            return str(data)

    return Transformer(dict(data=True))