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
        PARSERS=','.join((parser_class, parser_class))
    )
    data=[b'"Hello, there!"', b'Dear John']

    transformer = ParseToCSVTransformerTask(parameters, data)

    output = transformer.run()

    LOGGER.debug('Transformed Data: %s', output)

    assert b'"Hello, there!"' in output[0]
    assert b'Dear John' in output[1]
