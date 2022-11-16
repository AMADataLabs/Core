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
        licensed_organizations = self._csv_to_dataframe(self._data[0])

        frictionless_licensing_organizations = licensed_organizations[list(ORGANIZATIONS_COLUMNS.keys())].rename(
            columns=ORGANIZATIONS_COLUMNS
        )

        frictionless_licensing_organizations = frictionless_licensing_organizations.drop_duplicates()

        frictionless_licensing_organizations["id"] = frictionless_licensing_organizations.apply(
            self._generate_id,
            axis=1
        )

        return [self._dataframe_to_csv(frictionless_licensing_organizations)]

    @classmethod
    def _generate_id(cls, licence_organization):
        name_hash = hashlib.md5(licence_organization['name'].encode('utf-8')).hexdigest()
        prefix = ''.join(str(ord(x) - 65) for x in re.sub('[^a-zA-Z0-9]', '', licence_organization['name']))[-3:]
        suffix = ''.join(str(ord(x) - 48) for x in name_hash)[-6:]

        return int(prefix + suffix)


@add_schema
@dataclass
class ArticlesTransformerParameters:
    execution_time: str = None


class ArticlesTransformerTask(CSVReaderMixin, CSVWriterMixin, Task):
    PARAMETER_CLASS = ArticlesTransformerParameters

    def run(self):
        articles = self._csv_to_dataframe(self._data[0])

        articles = articles.rename(columns=ARTICLES_COLUMNS)

        return [self._dataframe_to_csv(articles)]
