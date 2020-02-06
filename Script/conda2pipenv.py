import argparse
import logging
import re

import jinja2

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def main(args):
	conda_package_list_filename = args['in']
	pipfile_filename = args['out']
	pipfile_template_filename = args['template']
	pipfile = None

	try:
		pipfile = generate_pipfile_from_conda_package_list(conda_package_list_filename, pipfile_template_filename)
	except Exception as e:
		logger.exception('Unable to generate the Pipfile.')

	if pipfile:
		write_pipfile(pipfile_filename, pipfile)


def generate_pipfile_from_conda_package_list(conda_package_list_filename, pipfile_template_filename):
	conda_dependencies = read_conda_dependencies(conda_package_list_filename)
	pipfile_template = read_pipfile_template(pipfile_template_filename)

	return render_template(pipfile_template, conda_dependencies)


def write_pipfile(pipfile_filename, pipfile):
	with open(pipfile_filename, '>') as file:
		file.write(pipfile)


def read_conda_dependencies(conda_package_list_filename):
	packages = {}

	with open(conda_package_list_filename) as file:
		for line in file:
			variable, value = parse_conda_dependency(line)

			if variable:
				packages[variable] = value


def read_pipfile_template(pipfile_template_filename):
	template = None

	with open(pipfile_template_filename) as file:
		template = jinja2.Template(file.read())

	return template


def render_template(pipfile_template, conda_dependencies):
	names = sorted(conda_dependencies.keys())
	pipfile_dependencies = []
	python_version

	for name in names:
		if name == 'python':
			python_version = conda_dependencies[name]
		elif name == 'conda':
			pass
		else:
			pipfile_dependencies.append(f"name = '=={conda_dependencies[name]}'")

	return pipfile_template.render(packages=pipfile_dependencies, python_version=python_version)


def parse_conda_dependency(dependency):
	variable = None
	value = None

	if not dependency.startswith('#'):
		variable, value, _ = dependency.split('=')

	return variable, value


if __name__ == '__main__':
	ap = argparse.ArgumentParser()

	ap.add_argument('-i', '--in', required=True, help='Path to the Conda package list file.')
	ap.add_argument('-o', '--out', required=True, help='Path to the Pipenv package list file (Pipfile).')
	ap.add_argument('-t', '--template', required=True, help='Path to the Pipfile template.')

	args = vars(ap.parse_args())

	main(args)