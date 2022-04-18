#!/usr/bin/env python3

import os
from   pathlib import Path
import subprocess
import sys

import repo


def main(args):
    script_path = Path(args[0])
    args = args[1:]

    environment = repo.setup_pythonpath(script_path)

    run_args(args, environment)


def run_args(args, environment):
    return_code = subprocess.call(args, env=environment)

    exit(return_code)


if __name__ == '__main__':
    main(sys.argv)
