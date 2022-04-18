''' Mixin for assisting with generating parameters from task parameters and loading a plugin. '''
import logging

from   datalabs.plugin import import_plugin

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class PluginExecutorMixin:
    @classmethod
    def _get_plugin(cls, plugin_class_name, task_parameters):
        plugin_class = import_plugin(plugin_class_name)
        plugin_parameters = cls._get_plugin_parameters(plugin_class, task_parameters)
        LOGGER.debug('%s Plugin Parameters: %s', plugin_class.__name__, plugin_parameters)

        return plugin_class(plugin_parameters)

    @classmethod
    def _get_plugin_parameters(cls, plugin_class: type, task_parameters):
        fields = plugin_class.PARAMETER_CLASS.__dataclass_fields__.keys()
        parameters = {key:getattr(task_parameters, key) for key in task_parameters.__dataclass_fields__.keys()}

        if hasattr(task_parameters, "unknowns"):
            cls._merge_parameter_unknowns(parameters)
        else:
            cls._remove_unknowns(parameters, fields)

        return parameters

    @classmethod
    def _merge_parameter_unknowns(cls, parameters):
        unknowns = parameters.get("unknowns", {})
        parameters.update(unknowns)
        parameters.pop("unknowns")

    @classmethod
    def _remove_unknowns(cls, parameters, fields):
        for key in parameters:
            if key not in fields:
                parameters.pop(key)
