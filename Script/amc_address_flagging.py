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
    from datalabs.analysis.amc.address import AMCAddressFlagger

    AMCAddressFlagger().run()


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-p', '--password', required=False, help='Password for .xlsx output file.')
    args = vars(ap.parse_args())

    main(args)
