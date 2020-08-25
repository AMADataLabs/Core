#!/usr/bin/env python3

import argparse
import logging
import os

import repo

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def main(args):
    repo.configure()  # Setup the repo's PYTHONPATH

    _configure_app(args)

    _run_application()


def _configure_app(args):
    import app

    app.configure(args, relative_path=args['path'])


def _run_application():
    from   datalabs.etl.task import ETLTaskWrapper
    ETLTaskWrapper().run()


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('path', help='Path relative to Script/Environment of the .env template directory for this ETL.')
    args = vars(ap.parse_args())

    LOGGER.debug('Args: %s', args)

    main(args)
