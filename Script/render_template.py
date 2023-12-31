import argparse
import base64
import logging
from   pathlib import Path
import re

from datalabs.common.setup import FileGeneratorFilenames, SimpleFileGenerator

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def main(args):
    kwargs = {}

    if args['vars']:
        kwargs.update(parse_kwargs(args['vars'].split(',')))

    if args['var']:
        kwargs.update(parse_kwargs(args['var']))

    if args['b64var']:
        kwargs.update(parse_kwargs(args['b64var']), b64encode=True)

    render_template(args['template'], args['file'], **kwargs)


def parse_kwargs(kwarg_strings, b64encode=False):
    kwarg_regex = re.compile(r'\s*([a-zA-Z0-9_.]+)=([^$]+)')
    kwargs = {}

    for kwarg_string in kwarg_strings:
        match = kwarg_regex.match(kwarg_string)

        if match:
            key = match.group(1)
            value = match.group(2)

            if b64encode:
                key = key + '_b64'
                value = base64.b64encode(value.encode('utf8')).decode('utf8')

            kwargs[key] = value

    return kwargs


def render_template(template_path, result_path, **kwargs):
    LOGGER.info(f'Generating file {result_path} from template {template_path}')
    filenames = FileGeneratorFilenames(template=Path(template_path), output=Path(result_path))

    file_generator = SimpleFileGenerator(filenames, **kwargs)
    file_generator.generate()


if __name__ == '__main__':
    return_code = 0

    ap = argparse.ArgumentParser()
    ap.add_argument('-t', '--template', required=True, help='Template file path.')
    ap.add_argument('-f', '--file', required=True, help='File resulting from rendering the template.')
    ap.add_argument('-V', '--vars',
                    help='String of comma-separated <KEY>=<VALUE> pair used to resolve the template variables.')
    ap.add_argument('-v', '--var', action='append',
                    help='<KEY>=<VALUE> pair used to resolve the template variables.')
    ap.add_argument('-b', '--b64var', action='append',
                    help='<KEY>=<VALUE> equivalent to -v KEY_b64=b64encode(VALUE).')
    args = vars(ap.parse_args())

    try:
        return_code = main(args)
    except Exception as e:
        LOGGER.exception(f"Failed to render template {args['template']}.")
        return_code = 1

    exit(return_code)
