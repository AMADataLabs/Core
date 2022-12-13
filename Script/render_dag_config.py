import argparse
import base64
import logging
import os
from   pathlib import Path
import re

from   render_template import render_template

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def main(args):
    script_path = os.path.realpath(os.path.dirname(__file__))
    file = f"{script_path}/../Deploy/{args['project']}/{args['environment']}/{args['template']}.yaml"
    template = f"{file}.jinja"
    kwargs = {}

    if args['var']:
        kwargs.update(parse_kwargs(args['var']))

    render_template(template, file, **kwargs)


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


if __name__ == '__main__':
    return_code = 0

    ap = argparse.ArgumentParser()
    ap.add_argument('-e', '--environment', required=True, help='Environment ID (sbx,dev,tst,stg,itg,prd)')
    ap.add_argument('-p', '--project', required=True, help='Project name.')
    ap.add_argument('-t', '--template', required=True, help='DAG config template name.')
    ap.add_argument('-v', '--var', action='append',
                    help='<KEY>=<VALUE> pair used to resolve the template variables.')
    args = vars(ap.parse_args())

    try:
        return_code = main(args)
    except Exception as e:
        LOGGER.exception(f"Failed to render template {args['template']}.")
        return_code = 1

    exit(return_code)
