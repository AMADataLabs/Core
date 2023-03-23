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
        # LOGGER.debug('Parameters: %s', self._parameters)        
        
        concept = "306683007" # FIXME - pull in value dynamically?
        # concept = self._parameters.path["concept"] # FIXME - pull in value dynamically?

        with AWSClient("dynamodb") as db:
            results = db.execute_statement(
            Statement=f"SELECT * FROM \"{self._parameters.database_table}\" WHERE pk = 'CONCEPT:{concept}' AND begins_with(\"sk\", 'CPT:')"
        )

        if(results["Items"] == []):
            return "No SNOMED concept for the given ID."

        mappings = []
        for item in results["Items"]:
            mapping = {key:value['S'] for key, value in item.items()}
            mapping.pop("pk")
            mapping["cpt_code"] = mapping.pop("sk").replace("CPT:", "")
            mappings.append(mapping)

        # FIXME: Set above to this?

        print("this 123///")
        print(mappings)

        self._response_body = self._generate_response_body(query.all()) # This line is required

        
