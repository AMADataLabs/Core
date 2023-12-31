""" Release endpoint classes. """
from dataclasses import dataclass
from datetime import datetime
import logging

import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

from datalabs.access.api.task import (
    APIEndpointTask,
    InvalidRequest,
    ResourceNotFound,
    Unauthorized
)
from datalabs.access.cpt.api.authorize import ProductCode, AuthorizedAPIMixin
from datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@dataclass
class SearchParameters:
    max_results: int
    index: int
    keywords: list
    sections: list
    subsections: list
    updated_after_date: str
    updated_before_date: str
    exact_match: bool


# pylint: disable=too-many-instance-attributes
@add_schema(unknowns=True)
@dataclass
class KnowledgeBaseEndpointParameters:
    method: str
    path: dict
    query: dict
    index_host: str
    index_name: str
    authorization: dict
    index_port: str = "443"
    region: str = "us-east-1"
    unknowns: dict = None


class KnowledgeBaseEndpointTask(AuthorizedAPIMixin, APIEndpointTask):
    PARAMETER_CLASS = KnowledgeBaseEndpointParameters
    PRODUCT_CODE = ProductCode.KNOWLEDGE_BASE

    @classmethod
    def _get_client(cls, region, host, port):
        port = int(port)
        service = "aoss"
        credentials = boto3.Session().get_credentials()
        awsauth = AWS4Auth(
            credentials.access_key,
            credentials.secret_key,
            region,
            service,
            session_token=credentials.token,
        )

        return OpenSearch(
            hosts=[{"host": host, "port": port}],
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            timeout=15,
        )


class MapSearchEndpointTask(KnowledgeBaseEndpointTask):
    def run(self):
        current_year = datetime.now().year
        authorized = self._authorized(self._parameters.authorization["authorizations"], current_year)
        opensearch = self._get_client(self._parameters.region, self._parameters.index_host, self._parameters.index_port)

        if not authorized:
            raise Unauthorized(f"Not authorized for year {current_year}")

        search_parameters = self._get_search_parameters(self._parameters.query)

        self._response_body = self._query_index(opensearch, search_parameters, self._parameters.index_name)

    @classmethod
    def _get_search_parameters(cls, parameters: dict) -> SearchParameters:
        max_results = cls._get_max_results(parameters)
        index = cls._get_index(parameters)
        keywords = parameters.get("keyword", [])
        sections = parameters.get("section", [])
        subsections = parameters.get("subsection", [])
        updated_after_date = parameters.get("updated_after_date")
        updated_before_date = parameters.get("updated_before_date")
        exact_match = parameters.get("exact_match")

        if max_results < 1:
            raise InvalidRequest("Results must be greater than 0.")

        return SearchParameters(
            max_results,
            index,
            keywords,
            sections,
            subsections,
            updated_after_date,
            updated_before_date,
            exact_match
        )

    @classmethod
    def _get_max_results(cls, parameters):
        max_results = 30

        if parameters.get("results") and len(parameters.get("results")) > 0:
            try:
                max_results = int(parameters.get("results")[0])
            except ValueError as error:
                raise InvalidRequest("Non-integer 'results' parameter value") from error

        return max_results

    @classmethod
    def _get_index(cls, parameters):
        index = 0

        if parameters.get("index") and len(parameters.get("index")) > 0:
            try:
                index = int(parameters.get("index")[0])
            except ValueError as error:
                raise InvalidRequest("Non-integer 'index' parameter value") from error

        return index

    @classmethod
    def _query_index(cls, opensearch, search_parameters, index_name):
        return cls._get_search_results(opensearch, search_parameters, index_name)

    @classmethod
    def _get_search_results(cls, opensearch, search_parameters, index_name):
        query_parameters = cls._get_query_parameters(search_parameters)
        LOGGER.debug("Query Parameters:\n%s", query_parameters)
        results = {"total_records": 0}

        response = opensearch.search(index=index_name, body=query_parameters)
        LOGGER.debug("Query Results:\n%s", response)

        if response is not None and response.get("hits", {}).get("total", {}).get("value", 0) > 0:
            results["items"] = [cls._generate_search_result(hit) for hit in response["hits"]["hits"]]
            results["total_records"] = response.get("hits", {}).get("total", {}).get("value", 0)

        return results

    @classmethod
    def _generate_search_result(cls, hit):
        answer_preview = cls._generate_answer_preview(hit["_source"]["answer"])

        return {
            "article_id": hit["_source"]["article_id"],
            "section": hit["_source"]["section"],
            "subsection": hit["_source"]["subsection"],
            "question": hit["_source"]["question"],
            "answer": answer_preview,
            "updated_on": hit["_source"]["updated_on"],
        }

    @classmethod
    def _generate_answer_preview(cls, answer):
        answer_words = str(answer).split()

        return " ".join(answer_words[:20])

    @classmethod
    def _get_query_parameters(cls, search_parameters):
        query_parameters = {}

        cls._add_pagination(query_parameters, search_parameters)

        keywords, cpt_code_search = cls._generate_keywords(search_parameters)

        if cpt_code_search:
            query_parameters["query"] = cls._generate_cpt_code_query_section(keywords)
        else:
            query_parameters["query"] = cls._generate_query_section(search_parameters, keywords)

        query_parameters["sort"] = cls._generate_sort_section()

        return query_parameters

    @classmethod
    def _add_pagination(cls, query_parameters, search_parameters):
        query_parameters["from"] = search_parameters.index
        query_parameters["size"] = search_parameters.max_results

    @classmethod
    def _generate_query_section(cls, search_parameters, keywords):

        query = dict(bool=cls._generate_bool_section(search_parameters, keywords))

        return query

    @classmethod
    def _generate_cpt_code_query_section(cls, keywords):
        return dict(multi_match=cls._generate_multi_match_section(keywords))

    @classmethod
    def _generate_bool_section(cls, search_parameters, keywords):
        bool_section = {}

        if keywords is not None and len(keywords) > 0:
            bool_section["must"] = cls._generate_must_section(keywords)
            if not search_parameters.exact_match:
                cls._add_fuzzy_section(bool_section['must']['multi_match'])

        filters = cls._generate_filters(search_parameters)

        if len(filters) > 0:
            bool_section["filter"] = filters

        return bool_section

    @classmethod
    def _generate_keywords(cls, search_parameters):
        keywords = None
        cpt_code_search = False
        LOGGER.debug("search_parameters.keywords:\n%s", search_parameters.keywords)

        if len(search_parameters.keywords) > 0:
            if len(search_parameters.keywords) == 1 and search_parameters.keywords[0].isdigit():
                cpt_code_search = True
                search_parameters.keywords[0] = f"*{search_parameters.keywords[0]}*"

            keywords = "|".join(search_parameters.keywords)
            LOGGER.debug("Keywords to be searched are %s", keywords)

        return keywords, cpt_code_search

    @classmethod
    def _generate_must_section(cls, keywords):
        return dict(multi_match=cls._generate_multi_match_section(keywords))

    @classmethod
    def _generate_multi_match_section(cls, keywords):
        return dict(
            query=keywords,
            fields=["section^3000", "subsection^1000", "question^10000", "answer^5000"]
        )

    @classmethod
    def _add_fuzzy_section(cls, multi_match_dictionary):

        multi_match_dictionary['boost'] = 50
        multi_match_dictionary['analyzer'] = "stop"
        multi_match_dictionary['auto_generate_synonyms_phrase_query'] = True
        multi_match_dictionary['fuzzy_transpositions'] = True
        multi_match_dictionary['fuzziness'] = "AUTO"
        multi_match_dictionary['minimum_should_match'] = 1
        multi_match_dictionary['type'] = "best_fields"
        multi_match_dictionary['lenient'] = True

    @classmethod
    def _generate_filters(cls, search_parameters):
        filters = []

        section_filter = cls._get_section_filter(search_parameters.sections)
        if section_filter:
            filters += section_filter

        subsection_filter = cls._get_subsection_filter(search_parameters.subsections)
        if subsection_filter:
            filters += subsection_filter

        range_filter = cls._get_range_filter(search_parameters)
        if range_filter:
            filters += range_filter

        return filters

    @classmethod
    def _get_section_filter(cls, sections):
        section_filter = None

        if sections is not None and len(sections) > 0:
            section_filter = [dict(terms=dict(section=sections))]

        return section_filter

    @classmethod
    def _get_subsection_filter(cls, subsections):
        subsection_filter = None

        if subsections is not None and len(subsections) > 0:
            subsection_filter = [dict(terms=dict(subsection=subsections))]

        return subsection_filter

    @classmethod
    def _get_range_filter(cls, search_parameters):
        updated_on_range_section = cls._generate_range_section(search_parameters)
        range_filter = None

        if updated_on_range_section:
            range_filter = [dict(range=dict(updated_on=dict(updated_on_range_section)))]

        return range_filter

    @classmethod
    def _generate_range_section(cls, search_parameters):
        updated_date_section = {}

        if search_parameters.updated_after_date is not None and len(search_parameters.updated_after_date) > 0:
            updated_date_section["gte"] = search_parameters.updated_after_date[0]

        if search_parameters.updated_before_date is not None and len(search_parameters.updated_before_date) > 0:
            updated_date_section["lte"] = search_parameters.updated_before_date[0]

        return updated_date_section

    @classmethod
    def _generate_sort_section(cls):
        return dict(updated_on=dict(order="desc"))


class GetArticleEndpointTask(KnowledgeBaseEndpointTask):
    def run(self):
        article_id = self._parameters.path["id"]
        current_year = datetime.now().year
        authorized = self._authorized(self._parameters.authorization["authorizations"], current_year)
        opensearch = self._get_client(self._parameters.region, self._parameters.index_host, self._parameters.index_port)

        if not authorized:
            raise Unauthorized(f"Not authorized for year {current_year}")

        self._response_body = self._get_article(article_id, opensearch, self._parameters.index_name)

    @classmethod
    def _get_article(cls, article_id, opensearch, index_name):
        article = None

        query = {"query": {"match": {"article_id": article_id}}}

        response = opensearch.search(index=index_name, body=query)

        if response["hits"]["total"]["value"] > 0:
            first_match = response["hits"]["hits"][0]
            article = first_match["_source"]
        else:
            raise ResourceNotFound(f"Article {article_id} not found.")

        return article

    @classmethod
    def _get_article_id(cls, parameters: dict):
        return parameters.get("article_id")
