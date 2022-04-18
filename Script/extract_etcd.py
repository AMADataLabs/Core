import argparse
import logging
import os

import jinja2

from   datalabs.access.parameter.etcd import EtcdEnvironmentLoader

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def main(args):
    loader = EtcdEnvironmentLoader(dict(
        host=args['host'],
        username=args['username'],
        password=args['password'],
        prefix=args['prefix']
    ))

    loader.load()

    for key, value in os.environ.items():
        if key.startswith(args['prefix']):
            print(f"export {key}='{value}'")


if __name__ == '__main__':
    return_code = 0

    ap = argparse.ArgumentParser()
    ap.add_argument('-H', '--host', required=True, help='Etcd host.')
    ap.add_argument('-u', '--username', required=True, help='Etcd username.')
    ap.add_argument('-p', '--password', required=True, help='Etcd password.')
    ap.add_argument('-x', '--prefix', required=True, help='Etcd key prefix.')
    args = vars(ap.parse_args())

    try:
        return_code = main(args)
    except Exception as e:
        LOGGER.exception(f'Failed to load ConfigMap into etcd.')
        return_code = 1

    exit(return_code)
