""" Release endpoint classes. """
from   collections import defaultdict
from   dataclasses import dataclass
import logging

from   datalabs.access.api.task import APIEndpointTask, InvalidRequest, ResourceNotFound 
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


# pylint: disable=too-many-instance-attributes
@add_schema(unknowns=True)
@dataclass
class MapSearchEndpointParameters:
    method: str
    path: dict
    query: dict
    authorization: dict
    database_table: str
    unknowns: dict=None
    

class MapSearchEndpointTask(APIEndpointTask):
    PARAMETER_CLASS = MapSearchEndpointParameters

    def run(self):
        max_results, index, keywords = self._get_query_parameters(self._parameters.query)

        with AWSClient("dynamodb") as db:
            maps = self._get_maps(keywords, db)

        filtered_maps = self._filter_maps(maps, self._parameters.query.get("category"))

        self._response_body = self._generate_response(filtered_maps, index, max_results)

    def _get_query_parameters(self, parameters):
        max_results = int(parameters.get("results")[0]) if parameters.get("results") else 50
        index = int(parameters.get("index")[0]) if parameters.get("index") else 0
        keywords = parameters.get("keyword")

        if max_results < 1:
            raise InvalidRequest("Results must be greater 0.")
        if index < 0:
            raise InvalidRequest("Index must be 0 or greater.")

        return max_results, index, keywords

    def _get_maps(self, keywords, db):
        mapping_set = {}

        if keywords:
            for keyword in keywords:
                mapping_references = self._get_mapping_references_by_keyword(db, keyword)
                mapping_set.update(self._get_mappings_from_references(mapping_references["Items"], db))
        else:
            mapping_set = self._get_all_mappings(db)
            
        maps = [self._generate_map(mappings) for mappings in mapping_set.values()]  
        maps.sort(key=lambda x: x["concept"])

        return maps

    def _filter_maps(self, maps, categories):
        if categories:
            for map in maps:
                map["mappings"] = [m for m in map["mappings"] if m["category"] in categories]

        return maps

    def _generate_response(self, filtered_maps, index, max_results):
        items = dict(
            maps=filtered_maps[index:index + max_results],
            available=len(filtered_maps)
        )

        if len(filtered_maps) >= max_results - index and index + max_results < len(filtered_maps):
            items["next"] = "/snomed/maps/cpt?index=" + str(index + max_results) + "&results=" + str(max_results)

        return items

    def _get_mapping_references_by_keyword(self, db, keyword):
        mapping_references = db.execute_statement(
            Statement=f"SELECT * FROM \"CPT-API-snomed-sbx\".\"SearchIndex\" WHERE sk = 'KEYWORD:{keyword}'"       
        ) 

        return mapping_references

    def _get_mappings_from_references(self, keyword_items, db):
        mappings = defaultdict(list)

        for search_item in keyword_items:
            mapping = self._get_mapping_from_reference(search_item['pk']['S'], db)

            mappings[mapping["pk"]["S"]].append(mapping)

        return mappings

    def _get_all_mappings(self, db):
        mappings = defaultdict(list)

        for item in self._paginate(db, "SELECT * FROM \"CPT-API-snomed-sbx\" WHERE begins_with(\"sk\", 'CPT:')"):
            mappings[item["pk"]["S"]].append(item)

        return mappings

    def _generate_map(self, mapping_items):
        mappings = []
        concept = None

        for item in mapping_items:
            mapping = {key:value['S'] for key, value in item.items()}

            if not concept:
                concept = mapping["pk"].replace("CONCEPT:", "")
                snomed_descriptor = mapping["snomed_descriptor"]

            mappings.append(
                dict(
                    code=mapping["sk"].replace("CPT:", ""),
                    descriptor=mapping["cpt_descriptor"],
                    category=mapping["map_category"]
                )
            )

        return dict(
            concept=concept,
            descriptor=snomed_descriptor,
            mappings=mappings
        )

    def _get_mapping_from_reference(self, pksk, db):
        pk = pksk.rsplit(':', 2)[0]
        sk = pksk.split(':', 2)[2]

        results = db.execute_statement(
            Statement=f"SELECT * FROM \"CPT-API-snomed-sbx\" WHERE pk = '{pk}' AND sk = '{sk}'"
        )

        return results["Items"][0]

    def _paginate(self, db, statement):  
        results = db.execute_statement(Statement=statement)
        
        for item in results["Items"]: 
            yield item 
            
        while "NextToken" in results: 
            results = db.execute_statement(Statement=statement, NextToken=results["NextToken"]) 
            
            for item in results["Items"]: 
                yield item