from   pathlib import Path
import subprocess
import sys


if __name__ == '__main__':
    path = Path('Source/Python')
    sys.path.append(path)

    args = sys.argv[1:]

    subprocess.call(args)
