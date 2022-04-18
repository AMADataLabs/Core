""" source: datalabs.etl.extract """
import pytest

from datalabs.etl.extract import ExtractorTask


# pylint: disable=redefined-outer-name
def test_extractor_task(extractor):
    extractor.run()

    assert extractor.data


@pytest.fixture
def extractor():
    return Extractor(dict(thing=True))


class Extractor(ExtractorTask):
    def _extract(self):
        return self._parameters['thing']
