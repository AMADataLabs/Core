import argparse
import logging

import jinja2

from datalabs.environment.convert import Conda2PipenvEnvrionmentConverter

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def main(args):
	conda_package_list_filename = args['in']
	pipfile_filename = args['out']
	pipfile_template_filename = args['template']
	converter = Conda2PipenvEnvrionmentConverter(conda_package_list_filename, pipfile_template_filename)
	return_code = 0

	pipfile = converter.convert()

	if pipfile:
		write_pipfile(pipfile_filename, pipfile)
	else:
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
	ap.add_argument('-w', '--whitelist', required=True, help='Path to the whitelist file.')

	args = vars(ap.parse_args())

	return_code = main(args)

	exit(return_code)