""" Release endpoint classes. """
import logging
from dataclasses import dataclass

from datalabs.access.api.task import APIEndpointTask, InvalidRequest
from datalabs.access.aws import AWSClient
from datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class QueryObjectDictionary:
    def add_item(self, item_name, item_value):
        self.__setattr__(item_name, item_value)


# pylint: disable=too-many-instance-attributes
@add_schema(unknowns=True)
@dataclass
class MapSearchEndpointParameters:
    method: str
    path: dict
    query: dict
    keywords: list
    authorization: dict
    database_index: str
    sections: str
    subsections: str
    updated_date_from: str
    updated_date_to: str
    unknowns: dict = None


@dataclass
class SearchParameters:
    max_results: int
    index: int
    keywords: list
    sections: list
    subsections: list
    updated_date_from: str
    updated_date_to: str


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
        keywords = parameters.get("keywords") if parameters.get("keywords") else None
        sections = parameters.get("sections").split('|') if parameters.get("sections") else []
        subsections = parameters.get("subsections").split('|') if parameters.get("subsections") else []
        updated_date_from = parameters.get("updated_date_from") if parameters.get("updated_date_from") else None
        updated_date_to = parameters.get("updated_date_to") if parameters.get("updated_date_to") else None

        if max_results < 1:
            raise InvalidRequest("Results must be greater than 0.")

        if index < 0:
            raise InvalidRequest("Index must be 0 or greater.")

        return SearchParameters(max_results, index, keywords, sections, subsections, updated_date_from, updated_date_to)

    @classmethod
    def _query_index(cls, opensearch, search_parameters):
        index_name = 'kbsearch-index'
        if search_parameters.keywords is not None:
            query = "|".join(search_parameters.keywords)
        else:
            query = None
        results = None

        if search_parameters.keywords:
            results = cls._get_search_results(opensearch, query, index_name, search_parameters)

        return results

    @classmethod
    def _get_query_object(cls, query, search_parameters):
        fields_array = []
        search_string_object = QueryObjectDictionary()
        query_object = QueryObjectDictionary()
        updated_on_range_object = None
        filters_array = []

        if search_parameters.sections is not None and len(search_parameters.sections) > 0:
            section_terms_object = QueryObjectDictionary()
            section_terms_object.section = search_parameters.sections
            filter_object = QueryObjectDictionary()
            filter_object.terms = section_terms_object
            filters_array.append(filter_object)
        if search_parameters.subsections is not None and len(search_parameters.subsections) > 0:
            subsection_terms_object = QueryObjectDictionary()
            subsection_terms_object.subsection = search_parameters.subsections
            filter_object = QueryObjectDictionary()
            filter_object.terms = subsection_terms_object
            filters_array.append(filter_object)
        if search_parameters.updated_date_from is not None and len(search_parameters.updated_date_from) > 0:
            updated_on_range_object = QueryObjectDictionary()
            updated_on_range_object.gte = search_parameters.updated_date_from
        if search_parameters.updated_date_to is not None and len(search_parameters.updated_date_to) > 0:
            if updated_on_range_object is None:
                updated_on_range_object = QueryObjectDictionary()
            updated_on_range_object.lte = search_parameters.updated_date_to
        if updated_on_range_object is not None:
            filter_object = QueryObjectDictionary()
            filter_object.range = updated_on_range_object
            filters_array.append(filter_object)

        search_string_object.add_item("from", 0)
        search_string_object.add_item("size", 30)
        boolean_object = QueryObjectDictionary()
        multi_match_object = QueryObjectDictionary()
        if query is not None:
            multi_match_object.query = query
        multi_match_object.fields = [
            "section^10000",
            "subsection^1000",
            "question^10",
            "answer"
        ]
        multi_match_object.boost = 50
        multi_match_object.analyzer = "stop"
        multi_match_object.auto_generate_synonyms_phrase_query = True
        multi_match_object.fuzzy_transpositions = True
        multi_match_object.fuzziness = "AUTO"
        multi_match_object.minimum_should_match = 1
        multi_match_object.type = "best_fields"
        multi_match_object.lenient = True

        must_object = QueryObjectDictionary()
        must_object.multi_match = multi_match_object
        boolean_object.must = must_object
        if len(filters_array) > 0:
            boolean_object.filter = filters_array
        query_object.bool = boolean_object
        search_string_object.query = query_object

        return search_string_object

    @classmethod
    def _get_search_results(cls, opensearch, query, index_name, search_parameters):
        results = None
        query_parameters = cls._get_query_object(query, search_parameters)
        response = opensearch.search(index=index_name, body=query_parameters)

        if response is not None and response.get('hits', {}).get('total', {}).get('value', 0) > 0:
            # Extract and process the search results
            results = response['hits']['hits']

        return results
