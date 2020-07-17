""" source: datalabs.etl.extract """
import pytest

from datalabs.etl.extract import ExtractorTask
from datalabs.etl.task import ETLComponentParameters


# pylint: disable=redefined-outer-name
def test_extractor_task(extractor):
    extractor.run()

    assert extractor.data


@pytest.fixture
def extractor():
    return Extractor(ETLComponentParameters(database={}, variables=dict(thing=True)))


class Extractor(ExtractorTask):
    def _extract(self):
        return self._parameters.variables['thing']
