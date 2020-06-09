""" source: datalabs.etl.cpt.transform """
import logging

from   datalabs.etl.cpt.transform import CPTFileToCSVTransformer

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def test_transforming_cpt_files_to_csv():
    parser_class = 'test.datalabs.etl.cpt.parse.TestParser'
    configuration = dict(
        PARSERS=','.join((parser_class, parser_class))
    )

    transformer = CPTFileToCSVTransformer(configuration)

    data = transformer.transform(['Hello, there!', 'Dear John'])

    LOGGER.debug('Transformed Data: %s', data)

    assert '"Hello, there!"' in data[0]
    assert 'Dear John' in data[1]
