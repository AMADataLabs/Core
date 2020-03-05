#!/usr/bin/env python3

import os
from   pathlib import Path
import subprocess
import sys


def main(args):
    script_path = Path(args[0])
    args = args[1:]

    environment = setup_pythonpath(script_path)

    run_args(args, environment)


def setup_pythonpath(script_path):
    datalabs_pythonpath = generate_datalabs_pythonpath(script_path)
    environment = os.environ.copy()
    current_pythonpath = environment.get('PYTHONPATH')

    if current_pythonpath:
        environment['PYTHONPATH'] = os.pathsep.join([datalabs_pythonpath, current_pythonpath])
    else:
        environment['PYTHONPATH'] = datalabs_pythonpath

    return environment


def run_args(args, environment):
    return_code = subprocess.call(args, env=environment)

    exit(return_code)


def generate_datalabs_pythonpath(script_path):
    shared_source_path = str(script_path.parent.joinpath('../Source/Python').resolve())
    common_code_path = str(script_path.parent.joinpath('../Sandbox/CommonCode').resolve())
    common_model_code_path = str(script_path.parent.joinpath('../Sandbox/CommonModelCode').resolve())

    return os.pathsep.join([shared_source_path, common_code_path, common_model_code_path])


if __name__ == '__main__':
    main(sys.argv)
