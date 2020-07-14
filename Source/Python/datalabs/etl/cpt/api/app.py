""" Wrapper module for running the LoadCPT ETL Lambda function locally """
import logging

from   datalabs.etl.awslambda import ETLTaskWrapper
from   datalabs.etl.task import ETLTask
import settings  # pylint: disable=unused-import

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def main():
    event = None
    context = {"function_name": "CPTLoad"}

    LOGGER.info('Running LoadCPT Lambda function locally...')
    ETLTaskWrapper(ETLTask).run(None)

if __name__ == '__main__':
    main()
