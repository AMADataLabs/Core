import os
from   pathlib import Path
import subprocess
import sys


if __name__ == '__main__':
    environment = os.environ.copy()
    path = Path('Source/Python')
    args = sys.argv[1:]

    if environment.get('PYTHONPATH'):
        environment['PYTHONPATH'] += ';' + str(path)
    else:
        environment['PYTHONPATH'] = str(path)

    return_code = subprocess.call(args, env=environment)

    exit(return_code)
