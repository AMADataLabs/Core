import argparse
import json
import os
import subprocess
import sys

from   datalabs.plugin import import_plugin

import repo


def main(language, args):
    repo.configure()  # Setup the repo's PYTHONPATH

    runtime_args = _get_runtime_args(args)

    _configure_app(args)

    if language == "java":
        _run_java_task(runtime_args)
    else:
        _run_python_task(runtime_args)


def _get_runtime_args(args):
    if args["args"]:
        runtime_args = [sys.argv[0]] + args["args"]
    else:
        runtime_args = json.loads(args["event"] or "{}")

    return runtime_args


def _configure_app(args):
    import app
    variables = args["variable"]
    template_args = {}

    if not args["check"]:
        args["force"] = True

    if not args["script"]:
        args["build"] = True

    if variables:
        template_args = {v.split('=')[0]:v.split('=')[1] for v in variables}

    app.configure(template_args, relative_path=args["path"], name=args["task"], overwrite=args["force"], build=args["build"])


def _run_python_task(args):
    task_wrapper_class = import_plugin(os.environ['TASK_WRAPPER_CLASS'])
    task_wrapper = task_wrapper_class(parameters=args)

    return task_wrapper.run()


def _run_java_task(args):
    command = ["java",  "datalabs.tool.TaskRunner"]

    if isinstance(args, list):
        for arg in args:
            command += ["--arg", arg]
    elif isinstance(args, dict):
        command += ["--event", json.dumps(args)]

    subprocess.run(command)

if __name__ == '__main__':
    language = sys.argv.pop()

    ap = argparse.ArgumentParser()
    ap.add_argument(
        '-a', '--args', action='append', help='Command-line arguments to send to the task wrapper.'
    )
    ap.add_argument(
        '-b', '--build', action='store_true', required=False, help='Use templates from paths under Build/. (default)'
    )
    ap.add_argument(
        '-s', '--script', action='store_true', required=False, help='Template paths are with respect to Script/Environment/ instead of Build/.'
    )
    ap.add_argument(
        '-e', '--event', required=False, help='JSON event passed in as a single command-line argument.'
    )
    ap.add_argument(
        '-c', '--check', required=False, action='store_true', help='Check for an existing .env output file, and exit if it exists.'
    )
    ap.add_argument(
        '-f', '--force', required=False, action='store_true', help='Force overwritting of the resolved .env template. (default)'
    )
    ap.add_argument('-p', '--path', required=False, help='Path relative to Build/ to look for .env templates.')
    ap.add_argument('-t', '--task', required=True, help='Task name used to load environment template (base name of .env.jinja file).')
    ap.add_argument(
        '-v', '--variable', action='append', required=False, help='Template variable to set in the form name=value.'
    )
    args = vars(ap.parse_args())

    main(language, args)
