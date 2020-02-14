import argparse
import logging

import jinja2

import datalabs.environment.setup as setup

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


ENVIRONMENT_GENERATORS = {
    'pip': setup.PipEnvironmentGenerator,
    'pipenv': setup.PipenvEnvironmentGenerator,
    'conda': setup.CondaEnvironmentGenerator,
}


def main(args):
    validated_args = validate_args(args)

    generator = create_generator(validated_args)

    generator.generate()


def validate_args(args):
    if args['env'] not in ENVIRONMENT_GENERATORS:
        raise ValueError(f'Unsupported environment "{args["env"]}"')

    return args


def create_generator(args):
    environment = args['env']
    filenames = setup.GeneratorFilenames(
        package_list=args['in'],
        template=args['template'],
        configuration=args['out'],
        whitelist=args.get('whitelist')
    )
    python_version = args['python']

    return ENVIRONMENT_GENERATORS[environment](filenames, python_version)


if __name__ == '__main__':
    return_code = 0

    ap = argparse.ArgumentParser()
    ap.add_argument('-e', '--env', required=True, help='Environment to generate (pipenv, conda).')
    ap.add_argument('-i', '--in', required=True, help='Path to the package list.')
    ap.add_argument('-o', '--out', required=True, help='Path to the virtual environment config.')
    ap.add_argument('-t', '--template', required=True, help='Path to the virtual environment config template.')
    ap.add_argument('-w', '--whitelist', required=False, help='Path to the whitelist.')
    ap.add_argument('-p', '--python', required=False, default='3.7', help='Python version (defautl is 3.7).')
    args = vars(ap.parse_args())

    try:
        return_code = main(args)
    except Exception as e:
        logger.exception(f'Failed to generate configuration for environment "{args["env"]}"')
        return_code = 1

    exit(return_code)