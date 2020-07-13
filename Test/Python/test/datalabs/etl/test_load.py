import pytest

from datalabs.etl.load import LoaderTask


def test_loader_task(loader):
    loader.run()

    assert loader.data == True


@pytest.fixture
def loader():
    class Loader(LoaderTask):
        def _load(self, data):
            return str(data)

    return Loader(dict(data=True))