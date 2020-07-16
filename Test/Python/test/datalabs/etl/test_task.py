""" REPLACE WITH DOCSTRING """
import pytest

from datalabs.etl.task import ETLTask, ETLParameters
from datalabs.etl.transform import TransformerTask
from datalabs.etl.load import LoaderTask

def test_transformer_task(parameters):
    etl = ETLTask(parameters)

    etl.run()

    assert etl._extractor.data == True
    assert etl._transformer.data == 'True'
    assert etl._loader.data == 'True'


@pytest.fixture
def parameters():
    return ETLParameters(
        extractor=dict(CLASS='test.datalabs.etl.test_extract.Extractor', thing=True),
        transformer=dict(CLASS='test.datalabs.etl.test_transform.Transformer'),
        loader=dict(CLASS='test.datalabs.etl.test_load.Loader'),
    )
