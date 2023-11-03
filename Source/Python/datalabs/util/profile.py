''' Performance profiling utilities. '''
from datetime import datetime
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


# pylint: disable=unused-argument
def _xml_format_converter(path, key, value):
    if value is not None and type(value) is str:
        try:
            return key, int(value)
        except ValueError:
            if value.lower() == 'true':
                return key, True
            elif value.lower() == 'false':
                return key, False
            else:
                return key, value
    else:
        return key, value
