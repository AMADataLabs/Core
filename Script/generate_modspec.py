import argparse
from   collections import defaultdict
import importlib
import logging
from   pathlib import Path
import sys

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def main(args):
    module = importlib.import_module(args["module"])
    imported_modules = set(sys.modules)
    datalabs_modules = sorted([m for m in imported_modules if m.startswith('datalabs.')], reverse=True)
    modspec = '---\nmodspec:\n'
    packages = defaultdict(list)

    current_package = ""
    for fully_qualified_module in datalabs_modules:
        package, module = fully_qualified_module.rsplit('.', 1)
        if fully_qualified_module not in packages:
            packages[package].append(module)

        current_package = package

    for package, modules in packages.items():
        modspec += f'  - package: {package}\n    include:\n'

        for module in modules:
            modspec += f'      - {module}\n'

    print(modspec)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('module', help='Python module to crawl.')
    args = vars(ap.parse_args())

    main(args)
