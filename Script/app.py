import os
from pathlib import Path
import sys

import dotenv

import os
from   render_template import render_template


def configure(template_parameters, relative_path=None, name=None, overwrite=False, build=False):
    script_path = Path(sys.argv[0])
    script_name = script_path.name
    if name is not None:
        script_name = name + ".py"
    environment_path = Path(script_path.parent, 'Environment')
    if build:
        environment_path = Path(script_path.parent.parent, 'Build')
    dotenv_name = script_name.replace('.py', '.env')
    dotenv_path = Path(environment_path, relative_path or '', dotenv_name)
    template_name = script_name.replace('.py', '.env.jinja')
    template_path = Path(environment_path, relative_path or '', template_name)

    if not os.path.exists(dotenv_path) and not os.path.exists(template_path):
        raise FileNotFoundError(
            f'No configuration file template for task "{name}" in {environment_path.absolute()}.'
        )
    elif os.path.exists(dotenv_path) and not overwrite:
        raise FileExistsError(
            f'Rendered configuration file exists and --check was used.'
        )

    render_template(template_path, dotenv_path, **template_parameters)

    dotenv.load_dotenv(dotenv_path=dotenv_path)
