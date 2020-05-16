import argparse
import logging
import os
from   pathlib import Path
import re
import shutil
import sys

import jinja2

from datalabs.build.bundle import SourceBundle

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def main(args):
    script_path = Path(sys.argv[0])
    script_base_path = script_path.parent
    repository_path = os.path.join(script_base_path, '..')
    shared_source_path = os.path.join(repository_path, 'Source', 'Python')
    build_path = os.path.join(repository_path, 'Build', args['project'])
    app_path = os.path.join(build_path, 'app')
    modspec_path = os.path.join(build_path, 'modspec.yaml')

    os.makedirs(app_path, exist_ok=True)

    SourceBundle(modspec_path).copy(shared_source_path, app_path)

    copy_dependency_files()

    if args['serverless']:
        zip_bundle_directory()


def create_bundle_directory():
    os.mkdir()
    

def copy_source_files():
    pass


def copy_dependency_files():
    pass


def zip_bundle_directory():
    pass


if __name__ == '__main__':
    return_code = 0

    ap = argparse.ArgumentParser()
    ap.add_argument('-s', '--serverless', type=bool, default=False,
        help='Create a zip archive of the bundle for serverless deployment.')
    ap.add_argument('-f', '--force', type=bool, default=False, help='Overwrite the existing bundle.')
    ap.add_argument('project', help='Name of the project.')
    args = vars(ap.parse_args())
    LOGGER.info('Args: %s', args)

    try:
        return_code = main(args)
    except Exception as e:
        LOGGER.exception(f"Failed to create app bundle.")
        return_code = 1

    exit(return_code)
