import argparse
import base64
import logging
import os
from   pathlib import Path
import re
import tempfile

from   render_template import render_template
from   datalabs.deploy.config.dynamodb import ConfigMapLoader

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def main(args):
    script_path = os.path.realpath(os.path.dirname(__file__))
    template = f"{script_path}/../Deploy/{args['project']}/{args['environment']}/{args['template']}.yaml.jinja"
    kwargs = {}

    if args['var']:
        kwargs.update(parse_kwargs(args['var']))

    with tempfile.NamedTemporaryFile(suffix='.yaml', delete=True) as file:
        render_template(template, file.name, **kwargs)

        load_dynamodb(args['environment'], file.name, args["dry_run"])


def parse_kwargs(kwarg_strings):
    kwarg_regex = re.compile(r'\s*([a-zA-Z0-9_.]+)=([^$]+)')
    kwargs = {}

    for kwarg_string in kwarg_strings:
        match = kwarg_regex.match(kwarg_string)

        if match:
            key = match.group(1)
            value = match.group(2)

            kwargs[key] = value

    return kwargs

def load_dynamodb(environment, file, dry_run):
    loader = ConfigMapLoader(table=f"DataLake-configuration-{environment}")

    loader.load([file], dry_run=dry_run)


if __name__ == '__main__':
    return_code = 0

    ap = argparse.ArgumentParser()
    ap.add_argument('-e', '--environment', required=True, help='Environment ID (sbx,dev,tst,stg,itg,prd)')
    ap.add_argument('-p', '--project', required=True, help='Project name.')
    ap.add_argument('-t', '--template', required=True, help='DAG config template name.')
    ap.add_argument('-v', '--var', action='append',
                    help='<KEY>=<VALUE> pair used to resolve the template variables.')
    ap.add_argument(
        '-D', '--dry-run', required=False, action='store_true', help='Render DAG config template and quit.'
    )
    args = vars(ap.parse_args())

    try:
        return_code = main(args)
    except Exception as e:
        LOGGER.exception(f"Failed to render template {args['template']}.")
        return_code = 1

    exit(return_code)
