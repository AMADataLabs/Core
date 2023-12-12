""" Transformer to convert raw Intelligent Platform licensed organizations list to a curated organization list for
intelligent platform front-end validation"""
from   dataclasses import dataclass
import logging

from   datalabs.etl.csv import CSVReaderMixin, CSVWriterMixin
from   datalabs.etl.intelligent_platform.licensing.sync.column import ARTICLE_COLUMNS, ORGANIZATION_COLUMNS
from   datalabs.parameter import add_schema
from   datalabs.task import Task



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
        licensed_organizations, active_contract_organizations, contract_rights_organizations \
            = [self._csv_to_dataframe(data) for data in self._data]

        organizations = licensed_organizations.merge(active_contract_organizations, how="outer", on="Organization")
        organizations = organizations.merge(contract_rights_organizations, how="outer", on="Organization")

        organizations = organizations[list(ORGANIZATION_COLUMNS.keys())].rename(columns=ORGANIZATION_COLUMNS)

        organizations = organizations.drop_duplicates()

        return [self._dataframe_to_csv(organizations)]


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


@add_schema
@dataclass
class UserManagementOrganizationsTransformerParameters:
    execution_time: str = None


class UserManagementOrganizationsTransformerTask(CSVReaderMixin, CSVWriterMixin, Task):
    PARAMETER_CLASS = UserManagementOrganizationsTransformerParameters

    def run(self):
        merged_organizations, portal_only_organizations \
            = [self._csv_to_dataframe(data) for data in self._data]

        organizations = merged_organizations.merge(portal_only_organizations, how="inner", on="name")

        #organizations = organizations[list(ORGANIZATION_COLUMNS.keys())].rename(columns=ORGANIZATION_COLUMNS)

        organizations = organizations.drop_duplicates()

        return [self._dataframe_to_csv(organizations)]
