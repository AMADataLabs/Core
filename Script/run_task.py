import argparse
import json
import os
import sys

from   datalabs.plugin import import_plugin

import repo


def main(args):
    repo.configure()  # Setup the repo's PYTHONPATH

    runtime_args = _get_runtime_args(args)

    _configure_app(args)

    _run_application(runtime_args)


def _get_runtime_args(args):
    runtime_args = args["args"]

    if not runtime_args and args["event"]:
        runtime_args = json.loads(args["event"])

    return runtime_args


def _configure_app(args):
    import app
    variables = args["variable"]
    template_args = {}

    if variables:
        template_args = {v.split('=')[0]:v.split('=')[1] for v in variables}

    app.configure(template_args, relative_path=args["path"], name=args["task"], overwrite=args["force"], build=args["build"])


def _run_application(args):
    task_wrapper_class = import_plugin(os.environ['TASK_WRAPPER_CLASS'])
    task_wrapper = task_wrapper_class(parameters=args)

    return task_wrapper.run()


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-t', '--task', required=True, help='Task name used to load environment template.')
    ap.add_argument(
        '-b', '--build', action='store_true', required=False, help='Use templates from Build/ instead of Script/Environment/.'
    )
    ap.add_argument('-p', '--path', required=False, help='Path relative to Script/Environment to look for .env templates.')
    ap.add_argument(
        '-f', '--force', required=False, action='store_true', help='Force overwritting of the resolved .env template.'
    )
    ap.add_argument(
        '-v', '--variable', action='append', required=False, help='Template variable to set in the form name=value.'
    )
    ap.add_argument(
        '-a', '--args', required=False, help='Command-line arguments to send to the task wrapper.'
    )
    ap.add_argument(
        '-e', '--event', required=False, help='JSON event passed in as a single command-line argument.'
    )
    args = vars(ap.parse_args())

    main(args)
