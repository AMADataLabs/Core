""" Functions involved in triggering the execution of CPT ETLs. """
import os

import datalabs.plugin as plugin


def trigger_etl(event, context):
    status = 200
    message = "ETL successfull"

    try:
        etl = _instantiate_etl(context['function_name'])

        etl(configuration).run()
    except Exception as e:
        status = 500
        message = e.message

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": message,
        }),
    }


def _instantiate_etl(function_name):
    configuration = _generate_app_configuration(function_name)

    ETL = plugin.import_plugin(configuration['ETL'])

    etl =  ETL(configuration)

    if not hasattr(etl, 'run'):
        raise TypeError('ETL plugin class does not have a "run" method.')

    return etl




def _generate_app_configuration(function_name):
    etl_name = function_name.upper()
    variable_base_name = 'ETL_' + etl_name + '_'
    expected_function_name = os.environ[variable_base_name + 'LAMBDA_FUNCTION']
    configuration = None

    if function_name == expected_function_name:
        configuration = _generate_etl_configuration(variable_base_name)
    else:
        raise ValueError('Lambda Function Name Mismatch. Expected "{}" but got "{}".'.format(
                expected_function_name, function_name
        ))

    return configuration


def _generate_etl_configuration(variable_base_name):
    configuration = {
        name[len(variable_base_name):]:value
        for name, value in os.environ.items()
        if name.startswith(variable_base_name)
    }

    configuration['EXTRACTOR'] = _instantiate_etl_plugin(configuration, 'EXTRACTOR')
    configuration['LOADER'] = _instantiate_etl_plugin(configuration, 'LOADER')

    return configuration


def _instantiate_etl_plugin(etl_configuration, variable_name):
    plugin_configuration = _extract_and_remove_plugin_configuration(etl_configuration, variable_name)

    Plugin = plugin.import_plugin(etl_configuration[variable_name])

    return Plugin(plugin_configuration)


def _extract_and_remove_plugin_configuration(etl_configuration, variable_name):
    plugin_configuration = {}
    drop_names = []

    for name, value in etl_configuration.items():
        if name.startswith(variable_name) and name != variable_name:
            plugin_configuration[name[len(variable_name)+1:]] = value
            drop_names.append(name)

    for name in drop_names:
        etl_configuration.pop(name)

    return plugin_configuration
