""" common api class. """


def format_element_as_list(element):
    return [element] if isinstance(element, dict) else element
