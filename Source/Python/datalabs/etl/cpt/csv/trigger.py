""" Functions involved in triggering the execution of the ETL. """
from   dataclasses import dataclass
import os

import json

from   datalabs.etl.common.enum import ExtractorType, LoaderType
from   datalabs.etl.cpt.csv.app import ETL


def trigger_csv_etl(event, context):
    configuration = _load_configuration(context['function_name'])

    ETL(configuration).run()

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "scrape successfull",
            # "location": ip.text.replace("\n", "")
        }),
    }


def _load_configuration(function_name):
    configuration = None

    if function_name == os.environ['ETL_CSV_LAMBDA_FUNCTION']:
        configuration = _load_etl_configuration("CSV")
    elif function_name == os.environ['ETL_DATABASE_LAMBDA_FUNCTION']:
        configuration = _load_etl_configuration("DATABASE")

    return configuration


def _load_etl_configuration(etl_name):
    variable_base_name = f'ETL_{etl_name}_'

    return [name:value for name, value in os.environ.items() if name.startwith(variable_base_name)]
