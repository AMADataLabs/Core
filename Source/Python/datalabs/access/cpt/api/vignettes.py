""" Release endpoint classes. """
from   dataclasses import dataclass
from   datetime import datetime

import logging

from   datalabs.access.api.task import APIEndpointTask, ResourceNotFound, InvalidRequest, Unauthorized
from   datalabs.access.cpt.api.authorize import ProductCode, AuthorizedAPIMixin
from   datalabs.access.aws import AWSClient
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=too-many-instance-attributes
@add_schema(unknowns=True)
@dataclass
class MapLookupEndpointParameters:
    method: str
    path: dict
    query: dict
    authorization: dict
    database_table: str
    unknowns: dict=None


class MapLookupEndpointTask(AuthorizedAPIMixin, APIEndpointTask):
    PARAMETER_CLASS = MapLookupEndpointParameters
    PRODUCT_CODE = ProductCode.VIGNETTES

    def run(self):
        authorized = self._authorized(self._parameters.authorization["authorizations"], datetime.now().year)

        if not authorized:
            raise Unauthorized("Unauthorized")

        cpt_code, additional_information = self._get_query_parameters()
        mappings = self._get_mappings_for_code(cpt_code)

        self._response_body = self._generate_response(mappings, additional_information)

    def _get_query_parameters(self):
        if not self._parameters.path["cpt_code"] or not self._parameters.path["cpt_code"].isnumeric():
            raise InvalidRequest("Bad Request", 400)

        if self._parameters.query.get('additional_information'):
            if not (
                self._parameters.query.get('additional_information')[0].upper() == 'TRUE' or
                self._parameters.query.get('additional_information')[0].upper() == 'FALSE'
            ):
                raise InvalidRequest("Bad Request", 400)

        return self._parameters.path["cpt_code"], self._parameters.query.get('additional_information')

    def _get_mappings_for_code(self, code):
        with AWSClient("dynamodb") as dynamodb:
            results = dynamodb.execute_statement(
                Statement=f"SELECT * FROM \"{self._parameters.database_table}\" WHERE pk = 'CPT CODE:{code}'"
            )

        if results["Items"] == []:
            raise ResourceNotFound("No data available")

        return results["Items"]

    def _generate_response(self, mappings, additional_information):
        response = {
                "cpt_code": mappings[0]['pk']['S'].replace("CPT CODE:", ""),
                "typical_patient": mappings[0]['typical_patient']['S'],
                "pre_service_info": mappings[0]['pre_service_info']['S'],
                "intra_service_info": mappings[0]['intra_service_info']['S'],
                "post_service_info": mappings[0]['post_service_info']['S']
        }

        if (additional_information and additional_information[0].upper() == 'TRUE'):
            response.update(
                {
                    "ruc_reviewed_date": mappings[0]['ruc_reviewed_date']['S'],
                    "concept_id": mappings[0]['sk']['S'].replace("CONCEPT:", "")
                }
            )

        return response
