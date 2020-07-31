#!/usr/bin/env python3

import argparse
import logging
import os

import repo

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def main(args):
    repo.configure()  # Setup the repo's PYTHONPATH

    _configure_app(args)

    ETL().run(args)


def _configure_app(args):
    import app

    app.configure(args, relative_path=args['path'])


class ETL:
    def run(self, args):
        from datalabs.etl.task import ETLTask

        parameters = self._generate_parameters()

        LOGGER.debug('Parameters: %s', parameters)

        etl = ETLTask(parameters)

        etl.run()

    @classmethod
    def _generate_parameters(cls):
        from datalabs.etl.task import ETLParameters

        return ETLParameters(
            extractor=cls._generate_component_parameters(os.environ, "EXTRACTOR"),
            transformer=cls._generate_component_parameters(os.environ, "TRANSFORMER"),
            loader=cls._generate_component_parameters(os.environ, "LOADER"),
        )

    @classmethod
    def _generate_component_parameters(cls, variables, variable_base_name):
        LOGGER.debug('Variables: %s', variables)
        LOGGER.debug('Variable Base Name: %s', variable_base_name)
        parameters = {
            name[len(variable_base_name)+1:]:value
            for name, value in variables.items()
            if name.startswith(variable_base_name + '_')
        }

        return parameters


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('path', help='Path relative to Script/Environment of the .env template directory for this ETL.')
    # ap.add_argument('-p', '--path', metavar="KEY=VALUE", nargs='+', help="Path relative to Script/Environment of the .env template directory for this ETL.")
    args = vars(ap.parse_args())

    LOGGER.debug('Args: %s', args)

    main(args)
