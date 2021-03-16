import yaml
import importlib
import copy


def convert_none_to_str(data):
    if isinstance(data, list):
        data[:] = [convert_none_to_str(i) for i in data]
    elif isinstance(data, dict):
        for k, v in data.items():
            data[k] = convert_none_to_str(v)
    return None if data == 'None' else data


class ConfigParser:

    def __init__(self):
        super().__init__()
        self.configuration = None

 def get_configuration(self):
        pass


class YAMLConfigParser(ConfigParser):

    def __init__(self, configuration_filename: str):
        super().__init__()
        with open(configuration_filename) as stream:
            try:
                self.configuration = convert_none_to_str(yaml.safe_load(stream))
            except yaml.YAMLError as exc:
                print(exc)

    def get_configuration(self):
        return copy.copy(self.configuration)


if __name__ == '__main__':
    config_parser = YAMLConfigParser('spreadsheet_config.yaml')
    print(config_parser.get_configuration())