import argparse
import logging

import jinja2

from   datalabs.deploy.dynamodb.load import ConfigMapLoader

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def main(args):
    loader = ConfigMapLoader(dict(
        table=args['table'],
        dag=args['dag']
   ))

    loader.load(args['file'])


if __name__ == '__main__':
    return_code = 0

    ap = argparse.ArgumentParser()
    ap.add_argument('-t', '--table', required=True, help='DynamoDB table name.')
    ap.add_argument('-d', '--dag', required=True, help='DAG name.')
    ap.add_argument('-f', '--file', required=True, help='ConfigMap YAML file.')
    args = vars(ap.parse_args())

    try:
        return_code = main(args)
    except Exception as e:
        LOGGER.exception('Failed to load ConfigMap into DynamoDB table %s.', args["table"])
        return_code = 1

    exit(return_code)
