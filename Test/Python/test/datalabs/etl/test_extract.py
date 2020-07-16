""" REPLACE WITH DOCSTRING """
import pytest

from datalabs.etl.extract import ExtractorTask


def test_extractor_task(extractor):
    extractor.run()

    assert extractor.data == True


@pytest.fixture
def extractor():
    return Extractor(dict(thing=True))


class Extractor(ExtractorTask):
    def _extract(self):
        return self._parameters['thing']
