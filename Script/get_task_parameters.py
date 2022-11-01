""" Clear the status of a DAG and it's tasks """
import argparse
import logging
import pprint

from   datalabs.access.parameter.dynamodb import DynamoDBEnvironmentLoader

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def main(args):
    parameters = {}

    dynamodb_loader = DynamoDBEnvironmentLoader(dict(
        table=f'DataLake-configuration-{args["environment"]}',
        dag=args["dag"],
        task=args["task"]
    ))

    dynamodb_loader.load(environment=parameters)

    pprint.pprint(parameters)

if __name__ == '__main__':
    return_code = 0

    ap = argparse.ArgumentParser()
    ap.add_argument('-d', '--dag', required=True, help='DAG name')
    ap.add_argument('-e', '--environment', required=True, help='sbx, dev, tst, itg, or prd')
    ap.add_argument('-t', '--task', required=True, help='task ID')
    args = vars(ap.parse_args())

    try:
        return_code = main(args)
    except Exception as e:
        LOGGER.exception(f'Failed to get DAG task configuration.')
        return_code = 1

    exit(return_code)
