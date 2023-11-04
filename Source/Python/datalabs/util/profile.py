''' Performance profiling utilities. '''
from   datetime import datetime
import logging

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

def _xml_format_converter(path, key, value):
    return_value = None

    if value is not None and type(value) is str:
        try:
            return_value = int(value)
        except ValueError:
            return_value = _convert_boolean_value(value)
    else:
        return_value = value

    return key, return_value

def _convert_boolean_value(value):
    if value.lower() == 'true':
        return True
    elif value.lower() == 'false':
        return False
    else:
        return value
