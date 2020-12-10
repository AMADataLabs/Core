""" source: datalabs.etl.cpt.transform """
from   dataclasses import dataclass
import logging

import pytest

from   datalabs.etl.cpt.api.transform import CSVToRelationalTablesTransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@pytest.mark.skip(reason="Used only for debugging")
def test_get_release_schedule(task):
    release_schedule = task._extract_release_schedule()

    assert len(release_schedule) == 5
    assert '1-Jan' in release_schedule


@pytest.fixture
def task():
    @dataclass
    class Parameters:
        database: dict

    parameters = Parameters(
        database=dict(
            name='sample',
            backend='postgresql+psycopg2',
            host='database-test-ui.c3mn4zysffxi.us-east-1.rds.amazonaws.com',
            username='DataLabs_UI',
            password='{{ password }}'
        )
    )

    return CSVToRelationalTablesTransformerTask(parameters)
