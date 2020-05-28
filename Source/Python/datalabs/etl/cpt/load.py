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

        self._database = None

    def load(self, data: transform.OutputData):
        with Database(configuration=Configuration.load('ORM'), credentials=Credentials.load('ORM')) as database:
            self._database = database

            self._update_tables(data)

    def _update_tables(self, data: transform.OutputData)
            self._update_codes(data.code)

            self._update_short_descriptors(data.short_descriptor)

            self._update_medium_descriptors(data.medium_descriptor)

            self._update_long_descriptors(data.long_descriptor)

            self._update_modifier_types(data.modifier_type)

            self._update_modifiers(data.modifier)

            self._update_consumer_descriptors(data.consumer_descriptor)

            self._update_clinician_descriptors(data.clinician_descriptor)

            self._update_clinician_descriptor_code_mappings(data.clinician_descriptor_code_mapping)

    def _start_database_session():
        connection_url = orm.generate_postgresql_url()

        return create_engine(connection_url, echo=True)



        # PSEUDO-CODE:
        #   * Get keys in data (a transform.OutputData instance)
        #   * Get classes in model module
        #   * Match data keys to table name of model classes
        #   * Get updatable, current data via ORM
        #   * For each data key
        #       * For each row in data[key]
        #           * Populate model class instance
        #           * Compare instance with current data
        #           * If row should be created, add instance via ORM
        #           * Else, update and re-add 
        #   * Commit class instances


    code: pandas.DataFrame
    short_descriptor: pandas.DataFrame
    medium_descriptor: pandas.DataFrame
    long_descriptor: pandas.DataFrame
    modifier_type: pandas.DataFrame
    modifier: pandas.DataFrame
    consumer_descriptor: pandas.DataFrame
    clinician_descriptor: pandas.DataFrame
    clinician_descriptor_code_mapping: pandas.DataFrame
