import os
from   pathlib import Path
import subprocess
import sys


if __name__ == '__main__':
    script_path = Path(sys.argv[0])
    environment = os.environ.copy()
    path = script_path.parent.joinpath('../Source/Python').resolve()
    args = sys.argv[1:]

    if environment.get('PYTHONPATH'):
        environment['PYTHONPATH'] += ';' + str(path)
    else:
        environment['PYTHONPATH'] = str(path)

    return_code = subprocess.call(args, env=environment)

    exit(return_code)
