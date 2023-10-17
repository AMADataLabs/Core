""" Release endpoint classes. """
import logging
from   dataclasses import dataclass

from   datalabs.access.api.task import APIEndpointTask, ResourceNotFound
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


class MapLookupEndpointTask(APIEndpointTask):
    PARAMETER_CLASS = MapLookupEndpointParameters

    def run(self):
        mappings = self._get_mappings_for_code(self._parameters.path["cpt_code"])

        self._response_body = self._generate_response(mappings)

    def _get_mappings_for_code(self, code):
        with AWSClient("dynamodb") as dynamodb:
            results = dynamodb.execute_statement(
                Statement=f"SELECT * FROM \"{self._parameters.database_table}\" WHERE pk = 'CPT CODE:{code}'"
        )

        if results["Items"] == []:
            raise ResourceNotFound("No Vignette for the given CPT Code")

        return results["Items"]

    def _generate_response(self, mappings):
        if (
        self._parameters.query.get('additional_information') and
        self._parameters.query.get('additional_information')[0].upper() == 'TRUE'
        ):
            response = {
                    "cpt_code": mappings[0]['pk']['S'].replace("CPT CODE:", ""),
                    "typical_patient": mappings[0]['typical_patient']['S'],
                    "pre_service_info": mappings[0]['pre_service_info']['S'],
                    "intra_service_info": mappings[0]['intra_service_info']['S'],
                    "post_service_info": mappings[0]['post_service_info']['S'],
                    "ruc_reviewed_date": mappings[0]['ruc_reviewed_date']['S'],
                    "concept_id": mappings[0]['sk']['S'].replace("CONCEPT:", "")
                }
        else:
            response = {
                "cpt_code": mappings[0]['pk']['S'].replace("CPT CODE:", ""),
                "typical_patient": mappings[0]['typical_patient']['S'],
                "pre_service_info": mappings[0]['pre_service_info']['S'],
                "intra_service_info": mappings[0]['intra_service_info']['S'],
                "post_service_info": mappings[0]['post_service_info']['S']
            }

        return response
