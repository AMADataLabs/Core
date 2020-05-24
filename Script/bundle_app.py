import argparse
import logging
import os
from   pathlib import Path
import re
import shutil
import sys
from   zipfile import ZipFile

import jinja2

from datalabs.build.bundle import SourceBundle

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def main(args):
    script_path = Path(sys.argv[0])
    script_base_path = script_path.parent
    repository_path = os.path.join(script_base_path, '..')
    shared_source_path = Path(os.path.join(repository_path, 'Source', 'Python')).resolve()
    build_path = Path(os.path.join(repository_path, 'Build', args['project'])).resolve()
    app_path = os.path.join(build_path, 'app')

    if not args['in_place']:
        LOGGER.info('=== Removing Old App Directory ===')
        shutil.rmtree(app_path)

        if args['serverless']:
            LOGGER.info('=== Copying Dependencies ===')
            copy_dependency_files(repository_path, app_path, args['project'])
        else:
            os.makedirs(app_path, exist_ok=True)

    LOGGER.info('=== Copying Build Files ===')
    copy_build_files(build_path, app_path)

    LOGGER.info('=== Copying Source Files ===')
    copy_source_files(build_path, shared_source_path, app_path)

    if args['verbose']:
        log_copied_source_files(shared_source_path, app_path, relative_file_paths)

    if args['serverless']:
        LOGGER.info('=== Creating Zip Archive ===')
        zip_bundle_directory(build_path, app_path)


def copy_dependency_files(repository_path, app_path, project):
    site_packages_path = os.path.join(repository_path, 'Environment', project, 'lib', 'python3.7', 'site-packages')

    shutil.copytree(site_packages_path, app_path)


def copy_build_files(build_path, app_path):
    copy_alembic_files(build_path, app_path)

    shutil.copy(os.path.join(build_path, 'requirements.txt'), os.path.join(app_path, 'requirements.txt'))

    shutil.copy(os.path.join(build_path, 'settings.py'), os.path.join(app_path, 'settings.py'))


def copy_source_files(build_path, shared_source_path, app_path):
    modspec_path = os.path.join(build_path, 'modspec.yaml')
    bundle = SourceBundle(modspec_path)

    return bundle.copy(shared_source_path, app_path)


def log_copied_source_files(shared_source_path, app_path, relative_file_paths):
    LOGGER.info('Copied the following files from')
    LOGGER.info(shared_source_path)
    LOGGER.info(f'    to {app_path}:')

    for file in relative_file_paths:
        LOGGER.info(file)


def zip_bundle_directory(build_path, app_path):
    archive_path = os.path.join(build_path, 'app.zip')

    os.remove(archive_path)

    with ZipFile(archive_path, 'w') as archive:
        archive.write('app')

        for contents in os.walk(app_path):
            archive_contents(archive, build_path, contents)


def copy_alembic_files(build_path, app_path):
    alembic_path = os.path.join(build_path, 'alembic')
    app_alembic_path = os.path.join(app_path, 'alembic')

    if os.path.exists(alembic_path):
        shutil.copytree(alembic_path, app_alembic_path)
        shutil.copyfile(alembic_path + '.ini', app_alembic_path + '.ini')


def archive_contents(archive, build_path, contents):
    root, dirs, files = contents
    relative_root = root.replace(str(build_path), '')[1:]
    LOGGER.debug('Build Path: %s', build_path)
    LOGGER.debug('Root Path: %s', root)
    LOGGER.debug('Relative Root Path: %s', relative_root)


    for d in dirs:
        archive.write(os.path.join(relative_root, d))

    for f in files:
        archive.write(os.path.join(relative_root, f))



if __name__ == '__main__':
    return_code = 0

    ap = argparse.ArgumentParser()
    ap.add_argument('-s', '--serverless', action='store_true', default=False,
        help='Create a zip archive of the bundle for serverless deployment.')
    ap.add_argument('-i', '--in-place', action='store_true', default=False,
        help='Do not pre-clean the app directory or try to install dependencies.')
    ap.add_argument('-v', '--verbose', action='store_true', default=False,
        help='Verbose output.')
    ap.add_argument('project', help='Name of the project.')
    args = vars(ap.parse_args())
    LOGGER.debug('Args: %s', args)

    try:
        return_code = main(args)
    except Exception as e:
        LOGGER.exception(f"Failed to create app bundle.")
        return_code = 1

    exit(return_code)
