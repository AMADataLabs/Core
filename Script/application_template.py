import argparse
import os

import repo


def main(args):
    repo.configure()  # Setup the repo's PYTHONPATH

    _configure_app(args)

    _run_application()


def _configure_app(args):
    import app

    app.configure(args)


def _run_application():
    raise NotImplementedError('Copy this template, remove this line, and modify this function as needed.')
    import datalabs.somepackage as myapp
    # or from datalabs.somepackage import MyApplication

    myapp.main()
    # or MyApplication().run()


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-s', '--secret', required=False, help='Super secret value')
    args = vars(ap.parse_args())

    main(args)
