""" Release endpoint classes. """
from   dataclasses import dataclass
import logging

from   datalabs.access.api.task import APIEndpointTask, ResourceNotFound
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


class MapLookupEndpointTask(APIEndpointTask):
    PARAMETER_CLASS = MapLookupEndpointParameters

    def run(self):
        mappings = self._get_mappings_for_concept(self._parameters.path["concept"])

        filtered_mappings = self._filter_mappings(mappings, self._parameters.query.get("category"))

        self._response_body = self._generate_response(filtered_mappings)

    def _get_mappings_for_concept(self, concept):
        with AWSClient("dynamodb") as db:
            results = db.execute_statement(
                Statement=f"""
                    SELECT * FROM \"{self._parameters.database_table}\" 
                    WHERE pk = 'CONCEPT:{concept}'
                    AND begins_with(\"sk\", 'CPT:')
                """
        )

        if results["Items"] == []:
            raise ResourceNotFound("No SNOMED concept for the given ID")
        
        return results["Items"]

    def _filter_mappings(self, mappings, categories):  
        filtered_mappings = mappings

        if categories:
            filtered_mappings = [mapping for mapping in filtered_mappings if mapping['map_category']['S'] in categories]

        return filtered_mappings

    def _generate_response(self, filtered_mappings):
        mappings = filtered_mappings

        if(filtered_mappings):
            mappings = {
                "concept": filtered_mappings[0]['pk']['S'].replace("CONCEPT:", ""),
                "descriptor": filtered_mappings[0]['snomed_descriptor']['S'],
                "mappings": []
            }

        for item in filtered_mappings:
            mapping = { 
                "code": item['sk']['S'].replace("CPT:", ""),
                "descriptor": item['cpt_descriptor']['S'].replace("CPT:", ""),
                "category": item['map_category']['S']
            }

            mappings["mappings"].append(mapping)

        return mappings