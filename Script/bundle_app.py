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
    shared_source_path = Path(os.path.join(repository_path, 'Source', 'Python')).resolve()
    build_path = os.path.join(repository_path, 'Build', args['project'])
    app_path = Path(os.path.join(build_path, 'app')).resolve()
    modspec_path = os.path.join(build_path, 'modspec.yaml')

    if not args['in_place']:
        LOGGER.info('=== Removing Old App Directory ===')
        shutil.rmtree(app_path)

        LOGGER.info('=== Copying Dependencies ===')
        copy_dependency_files(repository_path, app_path, args['project'])

    LOGGER.info('=== Copying Source Files ===')
    relative_file_paths = SourceBundle(modspec_path).copy(shared_source_path, app_path)

    # log_files_copied(shared_source_path, app_path, relative_file_paths)

    if args['serverless']:
        zip_bundle_directory()


def copy_dependency_files(repository_path, app_path, project):
    site_packages_path = os.path.join(repository_path, 'Environment', project, 'lib', 'python3.7', 'site-packages')

    shutil.copytree(site_packages_path, app_path)
    

def log_files_copied(shared_source_path, app_path, relative_file_paths):
    LOGGER.info('Copied the following files from')
    LOGGER.info(shared_source_path)
    LOGGER.info(f'    to {app_path}:')

    for file in relative_file_paths:
        LOGGER.info(file)


def zip_bundle_directory():
    pass


if __name__ == '__main__':
    return_code = 0

    ap = argparse.ArgumentParser()
    ap.add_argument('-s', '--serverless', action='store_true', default=False,
        help='Create a zip archive of the bundle for serverless deployment.')
    ap.add_argument('-i', '--in-place', action='store_true', default=False,
        help='Do not pre-clean the app directory or try to install dependencies.')
    ap.add_argument('project', help='Name of the project.')
    args = vars(ap.parse_args())
    LOGGER.debug('Args: %s', args)

    try:
        return_code = main(args)
    except Exception as e:
        LOGGER.exception(f"Failed to create app bundle.")
        return_code = 1

    exit(return_code)
