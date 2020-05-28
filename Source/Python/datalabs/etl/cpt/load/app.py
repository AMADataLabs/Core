""" Wrapper module for running the LoadCPT ETL Lambda function locally """
import logging

import datalabs.etl.run as run
import settings  # pylint: disable=unused-import

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def main():
    event = None
    context = {"function_name": "LoadCPT"}

    LOGGER.info('Running LoadCPT Lambda function locally...')
    run.lambda_handler(event, context)


if __name__ == '__main__':
    main()
