""" Clear the status of a DAG and it's tasks """
import argparse
import logging
import sys

from datalabs.deploy.config.dynamodb import Configuration

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=redefined-outer-name
def main(args):
    configuration = Configuration(f'DataLake-configuration-{args["environment"]}')

    for api in sorted(configuration.get_apis()):
        print(api)


# pylint: disable=invalid-name, broad-except
if __name__ == "__main__":
    return_code = 0

    ap = argparse.ArgumentParser()
    ap.add_argument("-e", "--environment", required=True, help="sbx, dev, tst, itg, or prd")
    args = vars(ap.parse_args())

    try:
        main(args)
    except Exception as e:
        LOGGER.exception("Failed to get APIs.")
        return_code = 1

    sys.exit(return_code)
