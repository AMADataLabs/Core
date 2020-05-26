""" CPT ETL Loader classes """
from   dataclasses import dataclass
import io
import logging

import pandas

from   datalabs.plugin import import_plugin
from   datalabs.etl.load import Loader
import datalabs.etl.cpt.dbmodel as model
import datalabs.etl.cpt.transform as transform

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class CPTRelationalTableLoader(Loader):
    def load(self, data):
        pass
