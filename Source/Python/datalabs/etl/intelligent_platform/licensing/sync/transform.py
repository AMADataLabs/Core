""" Transformer to convert raw Intelligent Platform licensed organizations list to a curated organization list for
intelligent platform front-end validation"""
from   dataclasses import dataclass
import logging

from   datalabs.etl.csv import CSVReaderMixin, CSVWriterMixin
from   datalabs.parameter import add_schema
from   datalabs.task import Task

from   datalabs.etl.intelligent_platform.licensing.sync.column import ARTICLE_COLUMNS, ORGANIZATION_COLUMNS


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

        organizations = self._fill_in_empty_licensees(organizations)

        organizations = organizations[list(ORGANIZATION_COLUMNS.keys())].rename(columns=ORGANIZATION_COLUMNS)

        organizations = organizations.drop_duplicates()

        return [self._dataframe_to_csv(organizations)]

    @classmethod
    def _fill_in_empty_licensees(cls, organizations):
        null_licensee_indicies = organizations.licensee.isnull()

        organizations.licensee[null_licensee_indicies] = organizations.OrganizationName[null_licensee_indicies]

        return organizations


@add_schema
@dataclass
class ArticlesTransformerParameters:
    execution_time: str = None


class ArticlesTransformerTask(CSVReaderMixin, CSVWriterMixin, Task):
    PARAMETER_CLASS = ArticlesTransformerParameters

    def run(self):
        articles = self._csv_to_dataframe(self._data[0])

        articles = articles[list(ARTICLE_COLUMNS.keys())].rename(columns=ARTICLE_COLUMNS)
        articles["lower_name"] = articles.article_name.str.lower()

        articles.drop_duplicates(subset=["lower_name"], inplace=True, keep="first")
        articles.drop(columns="lower_name", inplace=True)

        return [self._dataframe_to_csv(articles)]
