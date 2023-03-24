""" Release endpoint classes. """
from   dataclasses import dataclass
import logging

from   datalabs.access.api.task import APIEndpointTask, InvalidRequest
from   datalabs.parameter import add_schema
from   datalabs.access.aws import AWSClient

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

# pylint: disable=too-many-instance-attributes
@add_schema(unknowns=True)
@dataclass
class MapLookupEndpointParameters:
    path: dict
    query: dict
    authorization: dict
    database_table: str
    unknowns: dict=None

# change names first
class MapLookupEndpointTask(APIEndpointTask):
    PARAMETER_CLASS = MapLookupEndpointParameters

    def run(self):
        LOGGER.debug('Parameters: %s', self._parameters)     
        
        concept = self._parameters.path["concept"]
        if(self._parameters.query):
            passedFilter = self._parameters.query["category"]
        else:
            passedFilter = False

        with AWSClient("dynamodb") as db:
            results = db.execute_statement(
            Statement=f"SELECT * FROM \"{self._parameters.database_table}\" WHERE pk = 'CONCEPT:{concept}' AND begins_with(\"sk\", 'CPT:')"
        )

        if(results["Items"] == []):
            self._status_code = 404
            self._response_body = "No SNOMED concept for the given ID."
        else:
            mappings = {
                "concept": results["Items"][0]['pk']['S'].replace("CONCEPT:", ""),
                "descriptor": results["Items"][0]['snomed_descriptor']['S'],
                "mappings": []
            }

            for item in results["Items"]:

                mp = { 
                    "code": item['sk']['S'].replace("CPT:", ""),
                    "descriptor": item['cpt_descriptor']['S'].replace("CPT:", ""),
                    "category": item['map_category']['S']
                }

                # If there was no filter passed, add mp and we will add all of them
                if(not passedFilter):
                    mappings["mappings"].append(mp)
                # If there is a filter, this will execute and only add mp if in the filter category
                elif(mp["category"] in passedFilter):
                    mappings["mappings"].append(mp)

            self._response_body = []

        
