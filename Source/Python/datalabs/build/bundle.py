import logging

import yaml


logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class SourceBundle:
    def __init__(self, modspec_path):
        self._modspec_path = modspec_path

    def files(self, base_path):
        modspec_yaml = self._load_module_spec(self._modspec_path)

        modspec = self._parse_module_spec(modspec_yaml)

        return self._generate_module_paths(module_spec, base_path)

    @classmethod
    def _load_module_spec(cls, modspec_path) -> str:
        LOGGER.debug(f'Modspec path: {modspec_path}')
        modspec_yaml = None

        with open(modspec_path, 'r') as file:
            modspec_yaml = file.read()

        return modspec_yaml

    @classmethod
    def _parse_module_spec(cls, modspec_yaml) -> dict:
        modspec = yaml.safe_load(modspec_yaml)
        LOGGER.debug(f'Module spec: {modspec}')

        return modspec

    @classmethod
    def _generate_module_paths(cls, modspec, base_path):
        pass
        
