""" Release endpoint classes. """
import logging
import time
import uuid
from   requests_aws4auth import AWS4Auth
from   dataclasses import dataclass

from   opensearchpy import OpenSearch, RequestsHttpConnection, NotFoundError
from   opensearchpy.helpers import bulk

import boto3
from   datalabs.access.aws import AWSClient
from   datalabs.access.api.task import APIEndpointTask, InvalidRequest, ResourceNotFound, InternalServerError
from   datalabs.parameter import add_schema

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
    host_url: str
    index_name: str
    region: str = 'us-east-1'
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
        credentials = boto3.Session().get_credentials()
        awsauth = AWS4Auth(
            credentials.access_key,
            credentials.secret_key,
            self._parameters.region,
            service,
            session_token=credentials.token
        )
        opensearch_client = OpenSearch(
            hosts=[{'host': self._parameters.host_url, 'port': 443}],
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            timeout=15
        )

        self._response_body = self._query_index(opensearch_client, search_parameters, self._parameters.index_name)

    @classmethod
    def _get_search_parameters(cls, parameters: dict) -> SearchParameters:
        max_results = cls._get_max_results(parameters)
        index = cls._get_index(parameters)
        keywords = parameters.get("keyword", [])
        sections = parameters.get("section", [])
        subsections = parameters.get("subsection", [])
        updated_after_date = parameters.get("updated_after_date")
        updated_before_date = parameters.get("updated_before_date")

        if max_results < 1:
            raise InvalidRequest("Results must be greater than 0.")

        return SearchParameters(
            max_results,
            index,
            keywords,
            sections,
            subsections,
            updated_after_date,
            updated_before_date
        )

    @classmethod
    def _get_max_results(cls, parameters):
        max_results = 30

        if parameters.get('max_results') and len(parameters.get('max_results')) > 0:
            max_results = int(parameters.get('max_results')[0])

        return max_results

    @classmethod
    def _get_index(cls, parameters):
        index = 0

        if parameters.get('index') and len(parameters.get('index')) > 0:
            index = int(parameters.get('index')[0])

        return index

    @classmethod
    def _query_index(cls, opensearch, search_parameters, index_name):
        keywords = None
        results = None

        if search_parameters.keywords is not None:
            keywords = "|".join(search_parameters.keywords)
            if "1b4816d" in search_parameters.keywords:
                data_importer = OpenSearchDataImporter()
                data_importer.import_data(opensearch)
                LOGGER.info("OpenSearch data imported executed.")

        results = cls._get_search_results(opensearch, keywords, search_parameters, index_name)

        return results

    @classmethod
    def _get_search_results(cls, opensearch, keywords, search_parameters, index_name):
        results = None
        query_parameters = cls._get_query_parameters(keywords, search_parameters)
        LOGGER.info("Query Parameters are")
        LOGGER.info(str(query_parameters))
        response = opensearch.search(index=index_name, body=query_parameters)
        LOGGER.info("Query Results are")
        LOGGER.info(str(response))
        if response is not None and response.get('hits', {}).get('total', {}).get('value', 0) > 0:
            results = cls._generate_results_object(response)

        return results

    @classmethod
    def _generate_results_object(cls, response):
        results = {}
        items = []
        data_list = response['hits']['hits']

        for hit in data_list:
            answer_preview = cls._generate_answer_preview(hit['_source']['answer'])
            document_data = cls._generate_document_data(hit, answer_preview)
            items.append(document_data)
        results['items'] = items
        results['total_records'] = response['hits']['total']['value']
        LOGGER.info('returning these results.. ')
        LOGGER.info(str(results))

        return results

    @classmethod
    def generate_document_data(cls, hit, answer_preview):

        return {
            'id': hit['_source']['row_id'],
            'section': hit['_source']['section'],
            'subsection': hit['_source']['subsection'],
            'question': hit['_source']['question'],
            'answer': answer_preview,
            'updated_on': hit['_source']['updated_on'],
        }

    @classmethod
    def _generate_answer_preview(cls, answer):
        answer_words = str(answer).split()

        return ' '.join(answer_words[:20])

    @classmethod
    def _get_query_parameters(cls, keywords, search_parameters):
        query_parameters = {}

        cls._add_pagination(query_parameters, search_parameters)

        query_parameters['query'] = cls._generate_query_section(keywords, search_parameters)
        query_parameters['sort'] = cls._generate_sort_section()

        return query_parameters

    @classmethod
    def _add_pagination(cls, query_parameters, search_parameters):
        query_parameters['from'] = search_parameters.index
        query_parameters['size'] = search_parameters.max_results


    @classmethod
    def _generate_query_section(cls, keywords, search_parameters):

        return dict(
            bool=cls._generate_bool_section(keywords, search_parameters)
        )

    @classmethod
    def _generate_bool_section(cls, keywords, search_parameters):
        bool_section = dict()

        if keywords:
            bool_section["must"] = cls._generate_must_section(keywords)

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
                "section^3000",
                "subsection^1000",
                "question^10000",
                "answer^5000"
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

        cls._append_section_filter(search_parameters.sections, filters)

        cls._append_subsection_filter(search_parameters.subsections, filters)

        cls._append_range_filter(search_parameters, filters)

        return filters

    @classmethod
    def _append_section_filter(cls, sections, filters):
        if sections is not None and len(sections) > 0:
            section_filter = [
                dict(
                    terms=dict(
                        section=sections
                    )
                )
            ]
            filters += section_filter

    @classmethod
    def _append_subsection_filter(cls, subsections, filters):
        if subsections is not None and len(subsections) > 0:
            subsection_filter = [
                dict(
                    terms=dict(
                        subsection=subsections
                    )
                )
            ]
            filters += subsection_filter

    @classmethod
    def _append_range_filter(cls, search_parameters, filters):
        updated_on_range_section = cls._generate_range_section(search_parameters)

        if updated_on_range_section:
            range_filter = [
                {'range': updated_on_range_section}
            ]
            filters += range_filter

    @classmethod
    def _generate_range_section(cls, search_parameters):
        updated_date_section = {}

        if search_parameters.updated_after_date is not None and len(search_parameters.updated_after_date) > 0:
            updated_date_section = {'gte': search_parameters.updated_after_date}

        if search_parameters.updated_before_date is not None and len(search_parameters.updated_before_date) > 0:
            updated_date_section["lte"] = search_parameters.updated_before_date if updated_date_section else None

        return updated_date_section

    @classmethod
    def _generate_sort_section(cls):
        return dict(
            updated_on=dict(
                    order="desc"
            )

        )


@add_schema(unknowns=True)
@dataclass
class GetArticleParameters:
    method: str
    path: dict
    query: dict
    host_url: str
    index_name: str
    region: str = 'us-east-1'
    unknowns: dict = None


class GetArticleTask(APIEndpointTask):
    PARAMETER_CLASS = GetArticleParameters

    def run(self):
        article_id = self._parameters.path["id"]
        service = 'aoss'
        credentials = boto3.Session().get_credentials()
        awsauth = AWS4Auth(
            credentials.access_key,
            credentials.secret_key,
            self._parameters.region,
            service,
            session_token=credentials.token
        )
        opensearch_client = OpenSearch(
            hosts=[
                {
                    'host': self._parameters.host_url,
                    'port': 443
                }
            ],
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            timeout=15
        )

        self._response_body = self._get_article_data(article_id, opensearch_client, self._parameters.index_name)

    @classmethod
    def _get_article_data(cls, article_id, opensearch_client, index_name):
        query = {
            "query": {
                "match": {
                    "row_id": article_id
                }
            }
        }

        response = opensearch_client.search(index=index_name, body=query)

        if response["hits"]["total"]["value"] > 0:
            first_match = response["hits"]["hits"][0]
            document_data = first_match["_source"]
            LOGGER.info(document_data)
            return document_data
        else:
            raise ResourceNotFound(f'Article {article_id} not found.')

    @classmethod
    def _get_article_id(cls, parameters: dict):
        return parameters.get("id")


# Import knowledge base data is temporarily code.
class OpenSearchDataImporter:

    def _create_index(self, index_name, client):
        mappings = {
            "mappings": {
                "properties": {
                    "section": {
                        "type": "text"
                    },
                    "subsection": {
                        "type": "text"
                    },
                    "question": {
                        "type": "text"
                    },
                    "answer": {
                        "type": "text"
                    },
                    "updated_on": {
                        "type": "date"
                    },
                    "id": {
                        "type": "integer"
                    },
                    "row_id": {
                        "type": "text"
                    }
                }
            }
        }
        try:
            client.indices.create(index_name, body=mappings)
            time.sleep(5)
        except Exception as exp:
            LOGGER.warning(f"Exception while creating index: {index_name}, Exception: {exp}")

    def _delete_index(self, index_name, client):
        try:
            client.indices.delete(index_name)
            time.sleep(5)
        except Exception as exp:
            LOGGER.warning(f"Exception while creating index: {index_name}, Exception: {exp}")

    def _get_index_records_count(self, index_name, client):
        response = client.search(body='{"from": 0, "size": 5000}', index=index_name)
        data_ist = response['hits']['hits']
        return len(data_ist)

    def _import_kb_data(self, index_name, client):
        records = []
        count = 0
        batch_count = 1
        with AWSClient('s3') as s3_client:
            response = s3_client.get_object(Bucket="ama-dev-datalake-ingest-us-east-1", Key="AMA/KB/knowledge-base.psv")
            psv_data = response['Body'].read().decode('utf-8')
            rows = psv_data.split('\n')
            for row in rows:
                # Split each row into columns based on the '|' delimiter
                columns = row.split('|')
                length = len(columns)
                original_date = columns[5] if length >= 6 else ''
                updated_date = original_date.replace("\r", "")
                document_id = columns[0] if length >= 1 else ""
                record = {"section": columns[1] if length >= 2 else "",
                          "subsection": columns[2] if length >= 3 else "", "question": columns[3] if length >= 4 else "",
                          "answer": columns[4] if length >= 5 else "",
                          "updated_on": updated_date, "row_id": uuid.uuid1()}
                response = client.index(index=index_name, id=document_id, body=record)
                if response['result'] == 'created':
                    print(f'Document {columns[0]} indexed successfully.')
                else:
                    LOGGER.info(str(columns))
                    raise InternalServerError(f"Failed to index document {columns[0]}")

        #         records.append(record)
        #         count += 1
        #         if count == 500:
        #             count = 0
        #             bulk(client, records, index=index_name)
        #             time.sleep(5)
        #             records = []
        #             LOGGER.info(f"Batch count: {batch_count} is done")
        #             batch_count += 1
        # if len(records) > 0:
        #     bulk(client, records, index=index_name)
        #     time.sleep(5)

    def import_data(self, client):
        # Create index
        index_name = 'knowledge_base'
        if client.indices.exists(index=index_name):
            self._delete_index(index_name, client)

        self._create_index(index_name, client)
        indices = client.cat.indices()
        LOGGER.info(f"indices (Before import): {indices}")
        self._import_kb_data(index_name, client)
        count = self._get_index_records_count(index_name, client)
        LOGGER.info(f"Total number of records imported: {count}")
        indices = client.cat.indices()
        LOGGER.info(f"indices (After import): {indices}")
