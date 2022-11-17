""" Clear the status of a DAG and it's tasks """
import argparse
import logging

from datalabs.deploy.config.dynamodb import Configuration

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def main(args):
    configuration = Configuration(f'DataLake-configuration-{args["environment"]}')

    for dag in sorted(configuration.get_dags()):
        print(dag)

if __name__ == '__main__':
    return_code = 0

    ap = argparse.ArgumentParser()
    ap.add_argument('-e', '--environment', required=True, help='sbx, dev, tst, itg, or prd')
    args = vars(ap.parse_args())

    try:
        return_code = main(args)
    except Exception as e:
        LOGGER.exception(f'Failed to get DAGs.')
        return_code = 1

    exit(return_code)
