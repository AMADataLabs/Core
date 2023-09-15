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
    keywords: str
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
        max_results = int(parameters.get("results")) if parameters.get("results") else 50
        index = parameters.get("index") if parameters.get("index") else None
        keywords = parameters.get("keywords") if parameters.get("keywords") else None
        sections = parameters.get("sections").split('|') if parameters.get("sections") else []
        subsections = parameters.get("subsections").split('|') if parameters.get("subsections") else []
        updated_date_from = parameters.get("updated_date_from") if parameters.get("updated_date_from") else None
        updated_date_to = parameters.get("updated_date_to") if parameters.get("updated_date_to") else None

        if max_results < 1:
            raise InvalidRequest("Results must be greater than 0.")
        if index is None:
            raise InvalidRequest("Invalid Index name. ")

        return SearchParameters(max_results, index, keywords, sections, subsections, updated_date_from, updated_date_to)

    @classmethod
    def _query_index(cls, opensearch, search_parameters):
        keywords = None
        results = None

        if search_parameters.keywords is not None:
            keywords = "|".join(search_parameters.keywords)

        if search_parameters.keywords:
            results = cls._get_search_results(opensearch, keywords, search_parameters)

        return results

    @classmethod
    def _get_search_results(cls, opensearch, query, search_parameters):
        results = None

        query_parameters = cls._get_query_parameters(query, search_parameters)
        response = opensearch.search(index=search_parameters.index, body=query_parameters)

        if response is not None and response.get('hits', {}).get('total', {}).get('value', 0) > 0:
            results = response['hits']['hits']

        return results

    @classmethod
    def _get_query_parameters(cls, keywords, search_parameters):
        query_parameters = {}

        cls._add_pagination(query_parameters, search_parameters)

        query_parameters['query'] = cls._generate_query_section(keywords, search_parameters)

        return query_parameters

    @classmethod
    def _add_pagination(cls, query_parameters, search_parameters):
        query_parameters['from'] = 0
        query_parameters['size'] = 30

    @classmethod
    def _generate_query_section(cls, keywords, search_parameters):

        return dict(
            bool=cls._generate_bool_section(keywords, search_parameters)
        )

    @classmethod
    def _generate_bool_section(cls, keywords, search_parameters):
        bool_section = dict(
            must=cls._generate_must_section(keywords, search_parameters)
        )

        filter_array = cls._generate_filter_section(search_parameters)

        if len(filter_array) > 0:
            bool_section["filter"] = filter_array

        return bool_section

    @classmethod
    def _generate_must_section(cls, keywords, search_parameters):
        return dict(
            multi_match=cls._generate_multi_match_section(keywords, search_parameters)
        )

    @classmethod
    def _generate_multi_match_section(cls, keywords, search_parameters):
        return dict(
            fields=[
                "section^10000",
                "subsection^1000",
                "question^10",
                "answer"
            ],
            boost=50,
            analyzer="stop",
            auto_generate_synonyms_phrase_query=True,
            fuzzy_transpositions=True,
            fuzziness="AUTO",
            minimum_should_match=1,
            type="best_fields",
            lenient=True
        )

    @classmethod
    def _generate_filter_section(cls, search_parameters):
        filters_array = []

        if search_parameters.sections is not None and len(search_parameters.sections) > 0:
            filters_array.append(cls._generate_section_filter_section(search_parameters.sections))

        if search_parameters.subsections is not None and len(search_parameters.subsections) > 0:
            filters_array.append(cls._generate_subsection_filter_section(search_parameters.subsections))

        updated_on_range_section = cls._generate_range_section(search_parameters)

        if updated_on_range_section is not None:
            filter_section = {'range': updated_on_range_section}
            filters_array.append(filter_section)

        return filters_array

    @classmethod
    def _generate_section_filter_section(cls, sections):

        return dict(
            terms=dict(
                section=sections
            )
        )

    @classmethod
    def _generate_subsection_filter_section(cls, subsections):

        return dict(
            terms=dict(
                subsection=subsections
            )
        )

    @classmethod
    def _generate_range_section(cls, search_parameters):
        updated_date_section = {}

        if search_parameters.updated_date_from is not None and len(search_parameters.updated_date_from) > 0:
            updated_date_section = {'gte': search_parameters.updated_date_from}

        if search_parameters.updated_date_to is not None and len(search_parameters.updated_date_to) > 0:
            updated_date_section["lte"] = search_parameters.updated_date_to if updated_date_section else None

        return updated_date_section

