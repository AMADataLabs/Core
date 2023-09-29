""" Release endpoint classes. """
import logging
from   requests_aws4auth import AWS4Auth
from   dataclasses import dataclass

import boto3
from   datalabs.access.api.task import APIEndpointTask, InvalidRequest
from   datalabs.access.aws import AWSClient
from   datalabs.parameter import add_schema
from   opensearchpy import OpenSearch, RequestsHttpConnection

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
    collection_url: str
    unknowns: dict = None


@dataclass
class SearchParameters:
    max_results: int
    index: int
    keywords: list
    sections: list
    subsections: list
    updated_after_date: str
    updated_before_date: str


class MapSearchEndpointTask(APIEndpointTask):
    PARAMETER_CLASS = MapSearchEndpointParameters

    def run(self):
        try:
            search_parameters = self._get_search_parameters(self._parameters.query)
        except TypeError as type_error:
            raise InvalidRequest("Non-integer 'results' parameter value") from type_error
        service = 'aoss'
        region = 'us-east-1'
        credentials = boto3.Session().get_credentials()
        awsauth = AWS4Auth(credentials.access_key, credentials.secret_key,
                           region, service, session_token=credentials.token)
        opensearch_client = OpenSearch(
            hosts=[{'host': self._parameters.collection_url, 'port': 443}],
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            timeout=15
        )

        search_results = self._query_index(opensearch_client, search_parameters)

        return search_results

    @classmethod
    def _get_search_parameters(cls, parameters: dict) -> SearchParameters:
        max_results = int(parameters.get("results", 50))
        index = int(parameters.get("index", 0))
        keywords = parameters.get("keyword", [])
        sections = parameters.get("section", [])
        subsections = parameters.get("subsection", [])
        updated_after_date = parameters.get("updated_after_date")
        updated_before_date = parameters.get("updated_before_date")

        if max_results < 1:
            raise InvalidRequest("Results must be greater than 0.")

        if index is None:
            raise InvalidRequest("Invalid Index name. ")

        return SearchParameters(max_results, index, keywords, sections, subsections, updated_after_date, updated_before_date)

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
    def _get_search_results(cls, opensearch, keywords, search_parameters):
        results = None
        query_parameters = cls._get_query_parameters(keywords, search_parameters)

        response = opensearch.search(index=search_parameters.index, body=query_parameters)

        if response is not None and response.get('hits', {}).get('total', {}).get('value', 0) > 0:
            results = response['hits']['hits']

        return results

    @classmethod
    def _get_query_parameters(cls, keywords, search_parameters):
        query_parameters = {}

        cls._add_pagination(query_parameters)

        query_parameters['query'] = cls._generate_query_section(keywords, search_parameters)

        return query_parameters

    @classmethod
    def _add_pagination(cls, query_parameters):
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
            must=cls._generate_must_section(keywords)
        )

        filters = cls._generate_filters(search_parameters)

        if len(filters) > 0:
            bool_section["filter"] = filters

        return bool_section

    @classmethod
    def _generate_must_section(cls, keywords):
        return dict(
            multi_match=cls._generate_multi_match_section(keywords)
        )

    @classmethod
    def _generate_multi_match_section(cls, keywords):
        return dict(
            query=keywords,
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
    def _generate_filters(cls, search_parameters):
        filters = []

        filters += cls._generate_section_filter(search_parameters.sections)

        filters += cls._generate_subsection_filter(search_parameters.subsections)

        filters += cls._generate_range_filter(search_parameters)

        return filters

    @classmethod
    def _generate_section_filter(cls, sections):
        section_filter = []

        if sections is not None and len(sections) > 0:
            section_filter = [
                dict(
                    terms=dict(
                        section=sections
                    )
                )
            ]

        return section_filter

    @classmethod
    def _generate_subsection_filter(cls, subsections):
        subsection_filter = []

        if subsections is not None and len(subsections) > 0:
            subsection_filter = [
                dict(
                    terms=dict(
                        subsection=subsections
                    )
                )
            ]

        return subsection_filter

    @classmethod
    def _generate_range_filter(cls, search_parameters):
        range_filter = []

        updated_on_range_section = cls._generate_range_section(search_parameters)

        if updated_on_range_section is not None:
            range_filter = [
                {'range': updated_on_range_section}
            ]

        return range_filter

    @classmethod
    def _generate_range_section(cls, search_parameters):
        updated_date_section = {}

        if search_parameters.updated_after_date is not None and len(search_parameters.updated_after_date) > 0:
            updated_date_section = {'gte': search_parameters.updated_after_date}

        if search_parameters.updated_before_date is not None and len(search_parameters.updated_before_date) > 0:
            updated_date_section["lte"] = search_parameters.updated_before_date if updated_date_section else None

        return updated_date_section
