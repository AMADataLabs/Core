import pytest

from datalabs.etl.task import ETLTask
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
    return dict(
        EXTRACTOR_CLASS='test.datalabs.etl.test_extract.Extractor',
        EXTRACTOR_thing=True,
        TRANSFORMER_CLASS='test.datalabs.etl.test_transform.Transformer',
        LOADER_CLASS='test.datalabs.etl.test_load.Loader'
    )
