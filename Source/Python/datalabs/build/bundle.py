import logging

import yaml


logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class SourcesEmitter:
    @classmethod
    def emit(cls, modspec_path):
        module_spec = cls._load_module_spec(modspec_path)

        return cls._generate_module_paths(module_spec)

    @classmethod
    def _load_module_spec(cls, modspec_path):
        with open(yaml_path, 'r') as file:
            modspec = {}
            try:
                modspec = yaml.safe_load(stream)
            except yaml.YAMLError as e:
                LOGGER.error('Unable to load module spec file.', e)

        return modspec

    @classmethod
    def _load_module_spec(cls, modspec):
        
