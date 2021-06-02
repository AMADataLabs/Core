import argparse
import os
import sys

from   datalabs.plugin import import_plugin

import repo


def main(args):
    repo.configure()  # Setup the repo's PYTHONPATH

    _configure_app(args)

    _run_application()


def _configure_app(args):
    import app

    template_args = {v.split('=')[0]:v.split('=')[1] for v in args["variable"]}

    app.configure(template_args, name=args["task"], overwrite=args["force"])


def _run_application():
    task_wrapper_class = import_plugin(os.environ['TASK_WRAPPER_CLASS'])
    task_wrapper = task_wrapper_class(parameters=sys.argv)

    return task_wrapper.run()


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-t', '--task', required=True, help='Task name used to load environment template.')
    ap.add_argument(
        '-f', '--force', required=False, action='store_true', help='Force overwritting of the resolved .env template.'
    )
    ap.add_argument(
        '-v', '--variable', action='append', required=False, help='Template variable to set in the form name=value.'
    )
    args = vars(ap.parse_args())

    main(args)
