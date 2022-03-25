""" Oneview Residency Transformer"""
from   dataclasses import dataclass
import logging

from   datalabs.etl.csv import CSVReaderMixin, CSVWriterMixin
from   datalabs.etl.transform import TransformerTask
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@add_schema
@dataclass
class LicensedOrganizationsTransformerParameters:
    data: object = None

class LicensedOrganizationsTransformerTask(CSVReaderMixin, CSVWriterMixin, TransformerTask):
    PARAMETER_CLASS = LicensedOrganizationsTransformerParameters

    def _transform(self):
        licensed_organizations = self._csv_to_dataframe(self._parameters.data[0])

        frictionless_licensing_organizations = licensed_organizations[["OrganizationsUniqueID", "licensee"]].rename(
            columns=dict(OrganizationsUniqueID='id', licensee='name')
        )

        return [self._dataframe_to_csv(frictionless_licensing_organizations)]
