import os
from pathlib import Path
import sys

import dotenv

import os
from   render_template import render_template


def configure(template_parameters, relative_path=None):
    script_path = Path(sys.argv[0])
    script_name = script_path.name
    environment_path = Path(script_path.parent, 'Environment')
    dotenv_name = script_path.name.replace('.py', '.env')
    dotenv_path = Path(environment_path, relative_path or '', dotenv_name)
    template_name = script_path.name.replace('.py', '.jinja')
    template_path = Path(environment_path, relative_path or '', template_name)

    if not os.path.exists(dotenv_path) and not os.path.exists(template_path):
        raise FileNotFoundError(
            f'Application {script_name} does not have a configuration file in {environment_path.absolute()}.'
        )
    elif not os.path.exists(dotenv_path):
        render_template(template_path, dotenv_path, **template_parameters)

    dotenv.load_dotenv(dotenv_path=dotenv_path)
