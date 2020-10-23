import argparse
import logging
import os
from   pathlib import Path
import sys

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
    script_base_path = script_path.parent

    return Path(os.path.join(script_base_path, '..')).resolve()


if __name__ == '__main__':
    args = get_arguments()
    repository_path = get_repository_path()
    modspec_path = os.path.join(repository_path, 'Build', args['project'], 'modspec.yaml')
    shared_source_path = Path(os.path.join(repository_path, 'Source', 'Python')).relative_to(repository_path)
    bundle = SourceBundle(modspec_path)

    for file in bundle.files(shared_source_path):
        root_relative_path = os.path.join(shared_source_path, file)
        print(root_relative_path)
