""" CPT ETL Loader classes """
from   dataclasses import dataclass
import io
import logging

import pandas
import sqlalchemy

from datalabs.access.credentials import Credentials
from datalabs.access.database import Configuration
from datalabs.access.orm import Database
from   datalabs.plugin import import_plugin
from   datalabs.etl.load import Loader
import datalabs.etl.cpt.dbmodel as model
import datalabs.etl.cpt.transform as transform

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class CPTRelationalTableLoader(Loader):
    def __init__(self, configuration):
        super().__init__(configuration)

    def load(self, data: transform.OutputData):
        with Database(key='ORM') as database:
           self._session = database.session

            self._update_tables(data)

    def _update_tables(self, session, data: transform.OutputData)
            self._update_codes(data.code)

            self._update_short_descriptors(data.short_descriptor)

            self._update_medium_descriptors(data.medium_descriptor)

            self._update_long_descriptors(data.long_descriptor)

            self._update_modifier_types(data.modifier_type)

            self._update_modifiers(data.modifier)

            self._update_consumer_descriptors(data.consumer_descriptor)

            self._update_clinician_descriptors(data.clinician_descriptor)

            self._update_clinician_descriptor_code_mappings(data.clinician_descriptor_code_mapping)

    def _update_codes(self, table_data):
        current_codes = self._session.query(model.Code).all()
