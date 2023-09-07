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
    index: str
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

        query = None
        results = None
        if search_parameters.keywords is not None:
            query = "|".join(search_parameters.keywords)

        if search_parameters.keywords:
            results = cls._get_search_results(opensearch, query, search_parameters)

        return results

    @classmethod
    def _get_query_object(cls, query, search_parameters):

        search_string_object = dict()
        query_object = dict()
        filters_array = []

        if search_parameters.sections is not None and len(search_parameters.sections) > 0:
            filters_array.append(cls._get_section_filter_object(search_parameters.sections))
        if search_parameters.subsections is not None and len(search_parameters.subsections) > 0:
            filters_array.append(cls._get_subsection_filter_object(search_parameters.subsections))

        updated_on_range_object = cls._populate_updated_on_filters(search_parameters)

        if updated_on_range_object is not None:
            filter_object = dict()
            filter_object.range = updated_on_range_object
            filters_array.append(filter_object)

        search_string_object['from'] = 0
        search_string_object['size'] = 30
        boolean_object = dict()
        boolean_object.must = cls._get_multi_match_object(query)
        if len(filters_array) > 0:
            boolean_object.filter = filters_array
        query_object.bool = boolean_object
        search_string_object.query = query_object

        return search_string_object

    @classmethod
    def _get_search_results(cls, opensearch, query, search_parameters):

        results = None
        query_parameters = cls._get_query_object(query, search_parameters)
        response = opensearch.search(index=search_parameters.index, body=query_parameters)

        if response is not None and response.get('hits', {}).get('total', {}).get('value', 0) > 0:
            # Extract and process the search results
            results = response['hits']['hits']

        return results

    @classmethod
    def _get_section_filter_object(cls, sections):

        section_terms_object = dict()
        section_terms_object.section = sections
        filter_object = dict()
        filter_object.terms = section_terms_object

        return filter_object

    @classmethod
    def _get_subsection_filter_object(cls, subsections):

        subsection_terms_object = dict()
        subsection_terms_object.subsection = subsections
        filter_object = dict()
        filter_object.terms = subsection_terms_object

        return filter_object

    @classmethod
    def _populate_updated_on_filters(cls, search_parameters):

        updated_date_object = None
        if search_parameters.updated_date_from is not None and len(search_parameters.updated_date_from) > 0:
            updated_date_object = dict()
            updated_date_object.gte = search_parameters.updated_date_from
        if search_parameters.updated_date_to is not None and len(search_parameters.updated_date_to) > 0:
            if updated_date_object is None:
                updated_date_object = dict()
            updated_date_object.lte = search_parameters.updated_date_to
        return updated_date_object

    @classmethod
    def _get_multi_match_object(cls, query):

        multi_match_object = dict()
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
        must_object = dict()
        must_object.multi_match = multi_match_object
        return must_object
