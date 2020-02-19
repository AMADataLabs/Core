def key_finder(json_input, lookup_key):
    '''
    A geneator that recursively finds the next lookup_key's value in the possibly nested
    json input.
    '''
    if isinstance(json_input, dict):
        for key, value in json_input.items():
            if key == lookup_key:
                yield value
            else:
                yield from key_finder(value, lookup_key)
    elif isinstance(json_input, list):
        for item in json_input:
            yield from key_finder(value, lookup_key)

