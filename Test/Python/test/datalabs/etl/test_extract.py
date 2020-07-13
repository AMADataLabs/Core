import pytest

from datalabs.etl.extract import ExtractorTask


def test_extractor_task(extractor):
    extractor.run()

    assert extractor.data == dict(thing=True)


@pytest.fixture
def extractor():
    class Extractor(ExtractorTask):
        def _extract(self):
            return self._parameters

    return Extractor(dict(thing=True))