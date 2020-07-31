""" source: datalabs.etl.task """
import pytest

from datalabs.etl.task import ETLTask, ETLParameters, ETLComponentParameters


# pylint: disable=redefined-outer-name, protected-access
def test_transformer_task(parameters):
    etl = ETLTask(parameters)

    etl.run()

    assert etl._extractor.data
    assert etl._transformer.data == 'True'
    assert etl._loader.data == 'True'


@pytest.fixture
def parameters():
    return ETLParameters(
        extractor=ETLComponentParameters(
            database={},
            variables=dict(CLASS='test.datalabs.etl.test_extract.Extractor', thing=True)
        ),
        transformer=ETLComponentParameters(
            database={},
            variables=dict(CLASS='test.datalabs.etl.test_transform.Transformer')
        ),
        loader=ETLComponentParameters(
            database={},
            variables=dict(CLASS='test.datalabs.etl.test_load.Loader')
        )
    )
