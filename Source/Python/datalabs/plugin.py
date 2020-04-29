""" Helper functions for using plugins. """
import importlib


def import_plugin(plugin_name):
    module_name, class_name = plugin_name.rsplit('.', 1)
    module = importlib.import_module(module_name)

    return getattr(module, class_name)
