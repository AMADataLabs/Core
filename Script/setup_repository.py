#!/usr/bin/env python3

import logging
import os
from   pathlib import Path
import sys

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def main(args):
    script_path = Path(args[0])
    script_base_path = script_path.parent

    pythonpath = set_pythonpath(script_base_path)

    dotenv_templates = find_dotenv_templates(script_base_path)

    create_dotenv_files_from_templates(dotenv_templates, pythonpath)


def set_pythonpath(script_base_path):
    datalabs_pythonpath = generate_datalabs_pythonpath(script_base_path)

    for path in datalabs_pythonpath[::-1]:
        sys.path.insert(0, path)

    return os.pathsep.join(datalabs_pythonpath)


def find_dotenv_templates(script_base_path):
    search_directories = generate_search_directories(script_base_path)

    for search_directory in search_directories:
        template_path = Path(search_directory, 'env_template.txt')

        if os.path.isfile(template_path):
            yield template_path


def create_dotenv_files_from_templates(dotenv_templates, pythonpath):
    for dotenv_template in dotenv_templates:
        generate_dotenv_file_from_template(dotenv_template, pythonpath)


def generate_datalabs_pythonpath(script_base_path):
    shared_source_path = str(script_base_path.joinpath('../Source/Python').resolve())
    common_code_path = str(script_base_path.joinpath('../Sandbox/CommonCode').resolve())
    common_model_code_path = str(script_base_path.joinpath('../Sandbox/CommonModelCode').resolve())

    return [shared_source_path, common_code_path, common_model_code_path]


def generate_search_directories(script_base_path):
    sandbox_directory = os.sep.join(['..', 'Sandbox'])
    sandbox_walk_results = next(os.walk(Path(script_base_path, sandbox_directory)))

    return [Path(sandbox_walk_results[0], name).resolve() for name in sandbox_walk_results[1]]

def generate_dotenv_file_from_template(dotenv_template, pythonpath):
    from datalabs.common.setup import FileGeneratorFilenames, SimpleFileGenerator

    dotenv_path = Path(dotenv_template.parent, '.env')
    LOGGER.info(f'Generating dotenv file {str(dotenv_path)}')
    filenames = FileGeneratorFilenames(template=dotenv_template, output=dotenv_path)

    dotenv_generator = SimpleFileGenerator(filenames, pythonpath=pythonpath)
    dotenv_generator.generate()


if __name__ == '__main__':
    main(sys.argv)
