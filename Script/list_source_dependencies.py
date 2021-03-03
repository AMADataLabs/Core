import argparse
import logging
import os
import sys

from   pathlib import Path

from   datalabs.build.bundle import SourceBundle

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def get_arguments():
    ap = argparse.ArgumentParser()
    ap.add_argument('project', help='Name of the project.')
    args = vars(ap.parse_args())
    LOGGER.debug('Args: %s', args)

    return args


def get_repository_path():
    script_path = Path(sys.argv[0])
    script_base_path = script_path.resolve().parent

    return script_base_path.parent


if __name__ == '__main__':
    args = get_arguments()
    repository_path = get_repository_path()
    LOGGER.debug('Repository Path: %s', repository_path)
    modspec_path = os.path.join(repository_path, 'Build', args['project'], 'modspec.yaml')
    shared_source_path = repository_path.joinpath('Source', 'Python')
    bundle = SourceBundle(modspec_path)

    for file in bundle.files(shared_source_path):
        root_relative_path = shared_source_path.joinpath(file).relative_to(repository_path)
        print(root_relative_path)
