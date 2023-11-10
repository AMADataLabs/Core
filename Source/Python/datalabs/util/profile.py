''' Performance profiling utilities. '''
from   datetime import datetime
import logging
from   re import sub

import xmltodict

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def run_time_logger(func):
    def wrapper(*args, **kwargs):
        start = datetime.now().isoformat()
        LOGGER.info("start: %s @%s", start, func.__name__)

        result = func(*args, **kwargs)

        end = datetime.now().isoformat()
        LOGGER.info("end: %s @%s", end, func.__name__)

        return result

    return wrapper


def parse_xml_to_dict(xml):
    return xmltodict.parse(
        xml.decode("utf-8"),
        xml_attribs=False,
        postprocessor=_xml_format_converter
    )


# pylint: disable=unused-argument
def _xml_format_converter(path, key, value):
    return_value = None

    if value is not None and isinstance(value, str):
        try:
            return_value = int(value)
        except ValueError:
            return_value = _convert_boolean_value(value)
    else:
        return_value = value

    return _format_snake_case(key), return_value


def _convert_boolean_value(value):
    return_value = None

    if value.lower() == 'true':
        return_value = True
    elif value.lower() == 'false':
        return_value = False
    else:
        return_value = value

    return return_value


def _format_snake_case(text):
    return '_'.join(sub('([A-Z][a-z]+)', r' \1', sub('([A-Z]+)', r' \1', text.replace('-', ' '))).split()).lower()


def get_list_without_tags(original_list):
    objects = []

    if isinstance(original_list, dict):
        objects.append(original_list)
    else:
        objects = original_list

    return objects
