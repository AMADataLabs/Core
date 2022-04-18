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
    from datalabs.analysis.vertical_trail.physician_contact import sample

    sample.make_physician_contact_request_sample()


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    args = vars(ap.parse_args())

    main(args)
