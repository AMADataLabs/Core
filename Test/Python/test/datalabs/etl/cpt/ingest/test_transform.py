""" source: datalabs.etl.cpt.transform """
import logging

from   datalabs.etl.cpt.ingest.transform import CPTFileToCSVTransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=protected-access
def test_transforming_cpt_files_to_csv():
    parser_class = 'test.datalabs.etl.cpt.ingest.parse.TestParser'
    configuration = dict(
        PARSERS=','.join((parser_class, parser_class))
    )

    transformer = CPTFileToCSVTransformerTask(configuration)

    data = transformer._transform(['Hello, there!', 'Dear John'])

    LOGGER.debug('Transformed Data: %s', data)

    assert '"Hello, there!"' in data[0]
    assert 'Dear John' in data[1]
