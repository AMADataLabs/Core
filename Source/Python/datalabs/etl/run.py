""" Functions involved in triggering the execution of CPT ETLs. """
import json
import logging
import os

import datalabs.plugin as plugin

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=unused-argument
def lambda_handler(event, context):
    status = 200
    message = "ETL successfull"

    try:
        etl = _instantiate_etl(context['function_name'])

        etl.run()
    except Exception as exception:  # pylint: disable=broad-except
        LOGGER.error('Unable to instantiate ETL', exc_info=True)
        status = 500
        message = str(exception)

    return {
        "statusCode": status,
        "body": json.dumps({
            "message": message,
        }),
    }


def _instantiate_etl(function_name):
    configuration = _generate_app_configuration(function_name)

    LOGGER.info('Instantiating ETL app plugin %s', configuration['APP'])
    ETL = plugin.import_plugin(configuration['APP'])  # pylint: disable=invalid-name

    etl = ETL(configuration)

    if not hasattr(etl, 'run'):
        raise TypeError('ETL plugin class does not have a "run" method.')

    return etl




def _generate_app_configuration(function_name):
    etl_name = function_name.upper()
    variable_base_name = 'ETL_' + etl_name
    expected_function_name = os.environ[variable_base_name + '_LAMBDA_FUNCTION']
    configuration = _generate_configuration(os.environ, variable_base_name)

    if function_name == expected_function_name:
        configuration = _instantiate_plugins(configuration)
    else:
        raise ValueError('Lambda Function Name Mismatch. Expected "{}" but got "{}".'.format(
            expected_function_name, function_name
        ))

    return configuration


def _instantiate_plugins(configuration):
    for variable_base_name in ['EXTRACTOR', 'TRANSFORMER', 'LOADER']:
        plugin_configuration = _generate_configuration(configuration, variable_base_name)

        LOGGER.info('Instantiating ETL %s plugin %s', variable_base_name.lower(), configuration['APP'])
        configuration[variable_base_name] = _instantiate_plugin(configuration[variable_base_name], plugin_configuration)

    return configuration


def _generate_configuration(variables, variable_base_name):
    LOGGER.debug('Variables: %s', variables)
    LOGGER.debug('Variable Base Name: %s', variable_base_name)
    configuration = {
        name[len(variable_base_name)+1:]:value
        for name, value in variables.items()
        if name.startswith(variable_base_name + '_')
    }

    if not configuration:
        LOGGER.debug('Configuration: %s', configuration)
        LOGGER.warn(f'No configuration for "{variable_base_name}" in {variables}')

    return configuration


def _instantiate_plugin(plugin_class, configuration):
    Plugin = plugin.import_plugin(plugin_class)  # pylint: disable=invalid-name

    return Plugin(configuration)
