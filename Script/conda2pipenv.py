import argparse
import logging

import jinja2

from datalabs.environment.convert import Conda2PipenvEnvrionmentConverter, ConversionFilenames

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def main(args):
    filenames = ConversionFilenames(
        conda_package_list=args['in'],
        template=args['template'],
        converted_dependencies=args['out'],
        whitelist=args.get('whitelist')
    )
    converter = Conda2PipenvEnvrionmentConverter(filenames)
    return_code = 0

    try:
        converter.convert()
    except Exception as e:
        logger.exception('Failed to convert conda package list to Pipfile.')
        return_code = 1

    return return_code


def write_pipfile(pipfile_filename, pipfile):
    with open(pipfile_filename, 'w') as file:
        file.write(pipfile)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()

    ap.add_argument('-i', '--in', required=True, help='Path to the Conda package list file.')
    ap.add_argument('-o', '--out', required=True, help='Path to the Pipenv package list file (Pipfile).')
    ap.add_argument('-t', '--template', required=True, help='Path to the Pipfile template.')
    ap.add_argument('-w', '--whitelist', required=False, help='Path to the whitelist file.')

    args = vars(ap.parse_args())

    return_code = main(args)

    exit(return_code)