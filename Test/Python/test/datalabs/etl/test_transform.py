""" source: datalabs.etl.transform """
from   datalabs.etl.transform import PassThroughTransformerTask


def test_pass_through_transformer():
    transformer = PassThroughTransformerTask({}, [b'True'])

    data = transformer.run()


    assert data
    assert len(data) == 1
    assert data[0] == b'True'
