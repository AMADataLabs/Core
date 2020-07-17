""" source: datalabs.etl.cpt.transform """
import logging

from   datalabs.etl.cpt.ingest.transform import CPTFileToCSVTransformerTask
from   datalabs.etl.task import ETLComponentParameters

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=protected-access
def test_transforming_cpt_files_to_csv():
    parser_class = 'test.datalabs.etl.cpt.ingest.parse.TestParser'
    parameters = ETLComponentParameters(
        database={},
        variables=dict(
            PARSERS=','.join((parser_class, parser_class))
        ),
        data=['Hello, there!', 'Dear John']
    )

    transformer = CPTFileToCSVTransformerTask(parameters)

    data = transformer._transform()

    LOGGER.debug('Transformed Data: %s', data)

    assert '"Hello, there!"' in data[0]
    assert 'Dear John' in data[1]
