""" Transformer to convert raw Intelligent Platform licensed organizations list to a curated organization list for
intelligent platform front-end validation"""
from   dataclasses import dataclass
import hashlib
import logging
import re

from   datalabs.etl.csv import CSVReaderMixin, CSVWriterMixin
from   datalabs.parameter import add_schema
from   datalabs.task import Task

from   datalabs.etl.intelligent_platform.licensing.sync.column import ARTICLES_COLUMNS, ORGANIZATIONS_COLUMNS


logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@add_schema
@dataclass
class LicensedOrganizationsTransformerParameters:
    execution_time: str = None


class LicensedOrganizationsTransformerTask(CSVReaderMixin, CSVWriterMixin, Task):
    PARAMETER_CLASS = LicensedOrganizationsTransformerParameters

    def run(self):
        organizations = self._csv_to_dataframe(self._data[0])

        organizations = organizations[list(ORGANIZATIONS_COLUMNS.keys())].rename(columns=ORGANIZATIONS_COLUMNS)

        organizations = organizations.drop_duplicates()

        return [self._dataframe_to_csv(frictionless_licensing_organizations)]


@add_schema
@dataclass
class ArticlesTransformerParameters:
    execution_time: str = None


class ArticlesTransformerTask(CSVReaderMixin, CSVWriterMixin, Task):
    PARAMETER_CLASS = ArticlesTransformerParameters

    def run(self):
        articles = self._csv_to_dataframe(self._data[0])

        articles = articles.rename(columns=ARTICLES_COLUMNS).drop_duplicates()

        return [self._dataframe_to_csv(articles)]
