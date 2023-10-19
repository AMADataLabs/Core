""" Helper functions for using plugins. """
import importlib


def import_plugin(plugin_name):
    plugin_class = None

    if plugin_name:
        module_name, class_name = plugin_name.rsplit('.', 1)

        module = importlib.import_module(module_name)

        plugin_class = getattr(module, class_name)

    return plugin_class
