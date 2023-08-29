""" Release endpoint classes. """
import logging
from dataclasses import dataclass

from datalabs.access.api.task import APIEndpointTask, InvalidRequest
from datalabs.access.aws import AWSClient
from datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=too-many-instance-attributes
@add_schema(unknowns=True)
@dataclass
class MapSearchEndpointParameters:
    method: str
    path: dict
    query: dict
    keywords: list
    authorization: dict
    database_table: str
    database_index: str
    unknowns: dict = None


class MapSearchEndpointTask(APIEndpointTask):
    PARAMETER_CLASS = MapSearchEndpointParameters

    def run(self):
        max_results, index, keywords = self._get_query_parameters(self._parameters.query)
        search_results = None
        with AWSClient("opensearch") as opensearch_client:
            search_results = self._get_results(keywords, opensearch_client, max_results, index)

        return search_results

    @classmethod
    def _get_query_parameters(cls, parameters):
        max_results = int(parameters.get("results")[0]) if parameters.get("results") else 50
        index = int(parameters.get("index")[0]) if parameters.get("index") else 0
        keywords = parameters.get("keyword")

        if max_results < 1:
            raise InvalidRequest("Results must be greater 0.")
        if index < 0:
            raise InvalidRequest("Index must be 0 or greater.")

        return max_results, index, keywords

    @classmethod
    def _get_results(cls, keywords, opensearch_client, max_results, index):
        index_name = 'kbsearch-index'
        query_string = ''
        for keyword in keywords:
            query_string += f'|{keyword}'
        response = None
        if keywords:
            response = cls._get_search_results(query_string, opensearch_client, index_name, max_results, index)
        return response

    @classmethod
    def _get_search_results(cls, query_string, opensearch_client, index_name, max_results, index):

        search_query = {
            "from": index,
            "size": max_results,
            "query": {
                "multi_match": {
                    "query": f"{query_string}",
                    "fields": ['section^10000', 'subsection^1000', 'question^10', 'answer'],
                    "boost": 50,
                    "analyzer": "stop",
                    "auto_generate_synonyms_phrase_query": True,
                    "fuzzy_transpositions": True,
                    "fuzziness": "AUTO",
                    "minimum_should_match": 1,
                    "type": "best_fields",
                    "lenient": True,

                }
            }
        }
        response = opensearch_client.search(index=index_name, body=search_query)
        if response is not None and response.get('hits', {}).get('total', {}).get('value', 0) > 0:
            # Extract and process the search results
            return response['hits']['hits']
        return None
