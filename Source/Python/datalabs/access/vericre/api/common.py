""" common api class. """
from datalabs.access.api.task import InternalServerError


def format_element_as_list(element):
    return [element] if isinstance(element, dict) else element

def handle_exceptional_response(response):
    if response.status != 200:
        raise InternalServerError(f"Internal Server error caused by: {response.reason}, status: {response.status}")
