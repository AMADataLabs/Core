import os
from   pathlib import Path
import sys

def configure():
    script_path = Path(sys.argv[0])
    environment = setup_pythonpath(script_path)

    os.environ['PYTHONPATH'] = environment['PYTHONPATH']


def setup_pythonpath(script_path):
    datalabs_pythonpath = generate_datalabs_pythonpath(script_path)
    environment = os.environ.copy()
    current_pythonpath = environment.get('PYTHONPATH')

    if current_pythonpath:
        environment['PYTHONPATH'] = os.pathsep.join([datalabs_pythonpath, current_pythonpath])
    else:
        environment['PYTHONPATH'] = datalabs_pythonpath

    return environment


def generate_datalabs_pythonpath(script_path):
    shared_source_path = str(script_path.parent.joinpath('../Source/Python').resolve())
    common_code_path = str(script_path.parent.joinpath('../Sandbox/CommonCode').resolve())
    common_model_code_path = str(script_path.parent.joinpath('../Sandbox/CommonModelCode').resolve())
    shared_test_path = str(script_path.parent.joinpath('../Test/Python').resolve())

    return os.pathsep.join([shared_source_path, common_code_path, common_model_code_path, shared_test_path])
