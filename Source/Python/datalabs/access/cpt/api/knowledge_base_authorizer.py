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

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=too-many-instance-attributes
class KnowledgeBaseAuthorizer:
    @classmethod
    def _authorized(cls, authorizations):
        LOGGER.info(f"_authorized method of KnowledgeBaseAuthorizer class called.")
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
