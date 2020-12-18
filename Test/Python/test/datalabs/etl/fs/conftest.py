""" Pytest fixtures for test.datalabs.etl.fs """
import tempfile

import pytest


@pytest.fixture
def extractor_directory():
    with tempfile.TemporaryDirectory() as temp_directory:
        yield temp_directory


# pylint: disable=redefined-outer-name, line-too-long
@pytest.fixture
def extractor_file(extractor_directory):
    prefix = 'PhysicianProfessionalDataFile_2020120'

    with tempfile.NamedTemporaryFile(dir=extractor_directory, prefix=prefix+'1'):
        with tempfile.NamedTemporaryFile(dir=extractor_directory, prefix=prefix+'2') as file:
            file.write(
                """Driving west at dusk,
                The surest death is sunlight.
                Beautiful sunset.""".encode('UTF-8')
            )
            file.flush()

            yield file.name
