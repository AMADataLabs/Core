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

@dataclass
class SearchParameters:
    max_results: int
    index: str
    keywords: list


class MapSearchEndpointTask(APIEndpointTask):
    PARAMETER_CLASS = MapSearchEndpointParameters

    def run(self):
        search_parameters = self._get_search_parameters(self._parameters.query)
        search_results = None

        with AWSClient("opensearch") as opensearch:
            search_results = self._query_index(opensearch, search_parameters)

        return search_results

    @classmethod
    def _get_search_parameters(cls, parameters: dict) -> SearchParameters:
        max_results = int(parameters.get("results")[0]) if parameters.get("results") else 50
        index = int(parameters.get("index")[0]) if parameters.get("index") else 0
        keywords = parameters.get("keyword")

        if max_results < 1:
            raise InvalidRequest("Results must be greater 0.")

        if index < 0:
            raise InvalidRequest("Index must be 0 or greater.")

        return SearchParameters(max_results, index, keywords)

    @classmethod
    def _query_index(cls, opensearch, search_parameters):
        index_name = 'kbsearch-index'
        query = "|".join(search_parameters.keywords)
        results = None

        if search_parameters.keywords:
            results = cls._get_search_results(opensearch, query, index_name, search_parameters)

        return results

    @classmethod
    def _get_search_results(cls, opensearch, query, index_name, search_parameters):
        results = None

        query_parameters = {
            "from": search_parameters.index,
            "size": search_parameters.max_results,
            "query": {
                "multi_match": {
                    "query": f"{query}",
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

        response = opensearch.search(index=index_name, body=query_parameters)

        if response is not None and response.get('hits', {}).get('total', {}).get('value', 0) > 0:
            # Extract and process the search results
            results = response['hits']['hits']

        return results
