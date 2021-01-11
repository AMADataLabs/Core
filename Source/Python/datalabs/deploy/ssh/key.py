""" SSH key helper functions. """
import os


def load_key_from_variable(name, path):
    key = os.getenv(name)

    with open(path, 'w') as file:
        file.write('')

    os.chmod(path, 0o600)

    with open(path, 'w') as file:
        file.write(key)

    os.chmod(path, 0o400)
