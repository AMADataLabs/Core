import argparse
import logging

import jinja2

from   datalabs.environment.setup import EnvironmentGenerator

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def main(args):
    generator = EnvironmentGenerator.create(args)

    generator.generate()


if __name__ == '__main__':
    return_code = 0

    ap = argparse.ArgumentParser()
    ap.add_argument('-e', '--env', required=True, help='Environment to generate (pipenv, conda).')
    ap.add_argument('-i', '--in', required=True, help='Path to the package list.')
    ap.add_argument('-o', '--out', required=True, help='Path to the virtual environment config.')
    ap.add_argument('-t', '--template', required=True, help='Path to the virtual environment config template.')
    ap.add_argument('-w', '--whitelist', required=False, help='Path to the whitelist.')
    ap.add_argument('-p', '--python', required=False, default='3.7', help='Python version (defautl is 3.7).')
    args = vars(ap.parse_args())

    try:
        return_code = main(args)
    except Exception as e:
        logger.exception(f'Failed to generate configuration for environment "{args["env"]}"')
        return_code = 1

    exit(return_code)