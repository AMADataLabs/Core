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

    create_bundle_directory(args.project)

    copy_source_files()

    copy_dependency_files()

    if args.serverless:
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

    try:
        return_code = main(args)
    except Exception as e:
        LOGGER.exception(f"Failed to create app bundle.")
        return_code = 1

    exit(return_code)
