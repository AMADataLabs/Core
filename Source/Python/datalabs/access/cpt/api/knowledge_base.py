""" Release endpoint classes. """
import logging
import time
import uuid
import boto3
from   requests_aws4auth import AWS4Auth
from   dataclasses import dataclass
from   datetime import datetime, timezone

from   opensearchpy import OpenSearch, RequestsHttpConnection, NotFoundError
from   opensearchpy.helpers import bulk

from   datalabs.access.api.task import APIEndpointTask, InvalidRequest, ResourceNotFound, InternalServerError
from   datalabs.access.aws import AWSClient
from   datalabs.parameter import add_schema
from   datalabs.access.cpt.api.authorize import PRODUCT_CODE_KB
from   datalabs.access.cpt.api.knowledge_base_authorizer import KnowledgeBaseAuthorizer

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
    index_host: str
    index_name: str
    authorization: dict
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
        authorized = KnowledgeBaseAuthorizer.authorized(self._parameters.authorization["authorizations"])
        if authorized:
            try:
                search_parameters = self._get_search_parameters(self._parameters.query)
            except TypeError as type_error:
                raise InvalidRequest("Non-integer 'results' parameter value") from type_error

            opensearch_client = self._get_opensearch_client(
                self._parameters.region,
                self._parameters.index_host
            )

            self._response_body = self._query_index(
                opensearch_client,
                search_parameters,
                self._parameters.index_name
            )
        else:
            self._status_code = 401

    @classmethod
    def _authorized(cls, authorizations):
        authorized_years = cls._get_authorized_years(authorizations)
        LOGGER.info(f"Authorized years: {authorized_years}")
        authorized = False
        code_set = cls._get_current_year_code_set()
        LOGGER.info(f"Code Set: {code_set}")
        LOGGER.info(f"Authorizations: {str(authorizations)}")
        if datetime.now().year in authorized_years:
            authorized = True

        return authorized

    @classmethod
    def _get_current_year_code_set(cls):
        return f'{PRODUCT_CODE_KB}{str(datetime.now().year)[2:]}'

    @classmethod
    def _get_authorized_years(cls, authorizations):
        '''Get year from authorizations which are of one of the form:
            {PRODUCT_CODE}YY: ISO-8601 Timestamp
           For example,
            {PRODUCT_CODE}23: 2023-10-11T00:00:00-05:00
        '''
        cpt_api_authorizations = {key:value for key, value in authorizations.items() if cls._is_cpt_kb_product(key)}
        current_time = datetime.now(timezone.utc)
        authorized_years = []

        for product_code, period_of_validity in cpt_api_authorizations.items():
            authorized_years += cls._generate_authorized_years(product_code, period_of_validity, current_time)

        return authorized_years

    @classmethod
    def _is_cpt_kb_product(cls, product):
        return product.startswith(PRODUCT_CODE_KB)

    @classmethod
    def _generate_authorized_years(cls, product_code, period_of_validity, current_time):
        period_of_validity["start"] = datetime.fromisoformat(period_of_validity["start"]).astimezone(timezone.utc)
        period_of_validity["end"] = datetime.fromisoformat(period_of_validity["end"]).astimezone(timezone.utc)
        authorized_years = []

        if (
                product_code.startswith(PRODUCT_CODE_KB)
                and current_time >= period_of_validity["start"] <= current_time <= period_of_validity["end"]
        ):
            authorized_years += cls._generate_years_from_product_code(PRODUCT_CODE_KB, product_code)

        return authorized_years

    @classmethod
    def _generate_years_from_period(cls, period, current_time):
        years = list(range(period["start"].year, current_time.year + 1))

        if period["end"] <= current_time:
            years.pop()

        return years

    @classmethod
    def _generate_years_from_product_code(cls, base_product_code, product_code):
        authorized_years = []

        try:
            authorized_years.append(cls._parse_authorization_year(base_product_code, product_code))
        except ValueError:
            pass

        return authorized_years

    @classmethod
    def _parse_authorization_year(cls, base_product_code, product_code):
        two_digit_year = product_code[len(base_product_code):]

        return int('20' + two_digit_year)

    @classmethod
    def _get_opensearch_client(cls, region, index_host):
        service = 'aoss'
        credentials = boto3.Session().get_credentials()

        awsauth = AWS4Auth(
            credentials.access_key,
            credentials.secret_key,
            region,
            service,
            session_token=credentials.token
        )

        opensearch_client = OpenSearch(
            hosts=[{'host': index_host, 'port': 443}],
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            timeout=15
        )

        return opensearch_client

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
        LOGGER.info("search_parameters.keywords is ")
        LOGGER.info(str(search_parameters.keywords))
        if search_parameters.keywords is not None:
            LOGGER.info("search_parameters.keywords is not none")
            if len(search_parameters.keywords) == 1:
                LOGGER.info("Length of search_parameters.keywords is 1")
                if search_parameters.keywords[0].isdigit():
                    LOGGER.info("search_parameters.keywords is numeric")
                    keywords = f'*{search_parameters.keywords[0]}*'
                else:
                    keywords = search_parameters.keywords[0]
            else:
                LOGGER.info("Length of search_parameters.keywords > 1")
                keywords = "|".join(search_parameters.keywords)
            if "1b4816d" in search_parameters.keywords:
                data_importer = OpenSearchDataImporter()
                data_importer.import_data(opensearch)
                LOGGER.info("OpenSearch data imported executed.")

        LOGGER.info(f"Keywords to be searched are {str(keywords)}")
        results = cls._get_search_results(opensearch, keywords, search_parameters, index_name)

        return results

    @classmethod
    def _get_search_results(cls, opensearch, keywords, search_parameters, index_name):
        query_parameters = cls._get_query_parameters(keywords, search_parameters)
        LOGGER.info("Query Parameters are")
        LOGGER.info(str(query_parameters))
        results = {}

        response = opensearch.search(index=index_name, body=query_parameters)
        LOGGER.info("Query Results are")
        LOGGER.info(str(response))

        if response is not None and response.get('hits', {}).get('total', {}).get('value', 0) > 0:
            results['items'] = [cls._generate_search_result(hit) for hit in response['hits']['hits']]
            results['total_records'] = len(results['items'])
        else:
            results['total_records'] = 0

        return results

    @classmethod
    def _generate_search_result(cls, hit):

        answer_preview = cls._generate_answer_preview(hit['_source']['answer'])

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
            section_filter = [
                dict(
                    terms=dict(
                        section=sections
                    )
                )
            ]

        return section_filter

    @classmethod
    def _get_subsection_filter(cls, subsections):
        subsection_filter = None

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
    def _get_range_filter(cls, search_parameters):
        updated_on_range_section = cls._generate_range_section(search_parameters)
        range_filter = None

        if updated_on_range_section:
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
    index_host: str
    index_name: str
    region: str = 'us-east-1'
    unknowns: dict = None


class GetArticleTask(APIEndpointTask):
    PARAMETER_CLASS = GetArticleParameters

    def run(self):
        article_id = self._parameters.path["id"]
        service = 'aoss'

        credentials = boto3.Session().get_credentials()
        awsauth = self._get_aws4auth(self._parameters.region, credentials, service)
        opensearch_client = self._get_opensearch_client(self._parameters.index_host, awsauth)

        self._response_body = self._get_article(
            article_id,
            opensearch_client,
            self._parameters.index_name
        )

    @classmethod
    def _get_aws4auth(cls, region, credentials, service):

        return AWS4Auth(
            credentials.access_key,
            credentials.secret_key,
            region,
            service,
            session_token=credentials.token
        )

    @classmethod
    def _get_opensearch_client(cls, index_host, awsauth):

        return OpenSearch(
            hosts=[
                {
                    'host': index_host,
                    'port': 443
                }
            ],
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            timeout=15
        )

    @classmethod
    def _get_article(cls, article_id, opensearch_client, index_name):
        article = None

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
            article = first_match["_source"]
            LOGGER.info(article)
        else:
            raise ResourceNotFound(f'Article {article_id} not found.')

        return article

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
            time.sleep(2)
        except Exception as exp:
            LOGGER.warning(f"Exception while creating index: {index_name}, Exception: {exp}")

    def _delete_index(self, index_name, client):
        try:
            client.indices.delete(index_name)
            time.sleep(2)
        except Exception as exp:
            LOGGER.warning(f"Exception while creating index: {index_name}, Exception: {exp}")

    def _get_index_records_count(self, index_name, client):
        response = client.search(body='{"from": 0, "size": 5000}', index=index_name)
        hits = response['hits']['hits']
        return len(hits)

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
                    count += 1
                else:
                    LOGGER.info(str(columns))
                    raise InternalServerError(f"Failed to index document {columns[0]}")
            LOGGER.info(f'{count} documents have been indexed')
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


# class KnowledgeBaseAuthorizer:
#     @classmethod
#     def _authorized(cls, authorizations):
#         LOGGER.info(f"_authorized method of KnowledgeBaseAuthorizer class called.")
#         authorized_years = cls._get_authorized_years(authorizations)
#         LOGGER.info(f"Authorized years: {authorized_years}")
#         authorized = False
#         code_set = cls._get_current_year_code_set()
#         LOGGER.info(f"Code Set: {code_set}")
#         LOGGER.info(f"Authorizations: {str(authorizations)}")
#         if datetime.now().year in authorized_years:
#             authorized = True
#
#         return authorized
#
#     @classmethod
#     def _get_current_year_code_set(cls):
#         return f'{PRODUCT_CODE_KB}{str(datetime.now().year)[2:]}'
#
#     @classmethod
#     def _get_authorized_years(cls, authorizations):
#         '''Get year from authorizations which are of one of the form:
#             {PRODUCT_CODE}YY: ISO-8601 Timestamp
#            For example,
#             {PRODUCT_CODE}23: 2023-10-11T00:00:00-05:00
#         '''
#         cpt_api_authorizations = {key:value for key, value in authorizations.items() if cls._is_cpt_kb_product(key)}
#         current_time = datetime.now(timezone.utc)
#         authorized_years = []
#
#         for product_code, period_of_validity in cpt_api_authorizations.items():
#             authorized_years += cls._generate_authorized_years(product_code, period_of_validity, current_time)
#
#         return authorized_years
#
#     @classmethod
#     def _is_cpt_kb_product(cls, product):
#         return product.startswith(PRODUCT_CODE_KB)
#
#     @classmethod
#     def _generate_authorized_years(cls, product_code, period_of_validity, current_time):
#         period_of_validity["start"] = datetime.fromisoformat(period_of_validity["start"]).astimezone(timezone.utc)
#         period_of_validity["end"] = datetime.fromisoformat(period_of_validity["end"]).astimezone(timezone.utc)
#         authorized_years = []
#
#         if (
#                 product_code.startswith(PRODUCT_CODE_KB)
#                 and current_time >= period_of_validity["start"] <= current_time <= period_of_validity["end"]
#         ):
#             authorized_years += cls._generate_years_from_product_code(PRODUCT_CODE_KB, product_code)
#
#         return authorized_years
#
#     @classmethod
#     def _generate_years_from_period(cls, period, current_time):
#         years = list(range(period["start"].year, current_time.year + 1))
#
#         if period["end"] <= current_time:
#             years.pop()
#
#         return years
#
#     @classmethod
#     def _generate_years_from_product_code(cls, base_product_code, product_code):
#         authorized_years = []
#
#         try:
#             authorized_years.append(cls._parse_authorization_year(base_product_code, product_code))
#         except ValueError:
#             pass
#
#         return authorized_years
#
#     @classmethod
#     def _parse_authorization_year(cls, base_product_code, product_code):
#         two_digit_year = product_code[len(base_product_code):]
#
#         return int('20' + two_digit_year)
