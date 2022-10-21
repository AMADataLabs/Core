""" source: datalabs.etl.transform """
import pytest

from   datalabs.etl.transform import PassThroughTransformerTask
from   datalabs.task.Task


def test_pass_through_transformer():
    transformer = PassThroughTransformerTask({}, [b'True']))

    data = transformer.run()


    assert data
    assert len(data) == 1
    assert data[0] == b'True'
