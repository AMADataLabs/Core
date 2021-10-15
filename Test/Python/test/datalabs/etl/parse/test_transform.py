""" source: datalabs.etl.parse.transform """
import logging

from   datalabs.etl.parse.transform import ParseToCSVTransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=protected-access
def test_transforming_cpt_files_to_csv():
    parser_class = 'test.datalabs.etl.cpt.ingest.parse.TestParser'
    parameters = dict(
        PARSERS=','.join((parser_class, parser_class)),
        data=[b'"Hello, there!"', b'Dear John']
    )

    transformer = ParseToCSVTransformerTask(parameters)

    data = transformer._transform()

    LOGGER.debug('Transformed Data: %s', data)

    assert b'"Hello, there!"' in data[0]
    assert b'Dear John' in data[1]
