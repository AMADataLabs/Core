import argparse
import logging

import jinja2

from   datalabs.deploy.etcd.load import ConfigMapLoader

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def main(args):
    loader = ConfigMapLoader(dict(
        host=args['host'],
        username=args['username'],
        password=args['password']
    ))

    loader.load(args['file'])


if __name__ == '__main__':
    return_code = 0

    ap = argparse.ArgumentParser()
    ap.add_argument('-H', '--host', required=True, help='Etcd host.')
    ap.add_argument('-u', '--username', required=True, help='Etcd username.')
    ap.add_argument('-p', '--password', required=True, help='Etcd password.')
    ap.add_argument('-f', '--file', required=True, help='ConfigMap YAML file.')
    args = vars(ap.parse_args())

    try:
        return_code = main(args)
    except Exception as e:
        LOGGER.exception(f'Failed to load ConfigMap into etcd.')
        return_code = 1

    exit(return_code)
