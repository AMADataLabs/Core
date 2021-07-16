""" CPT Marketing transform """
from bisect import bisect_left, insort_left
import csv
from   io import BytesIO
import logging
import random
import string

import numpy as np
import pandas
from ipdb import sset_trace as st

import datalabs.etl.transform as etl

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class DashboardDataTransformerTask(etl.TransformerTask):
    MAX_ID_ATTEMPTS = 10

    def _transform(self):
        table_data = self._csv_to_dataframe(self._parameters['data'])

        st()
        input_directory, output_directory, tables = setup_directory()

        budget_code = import_budget_code(input_directory)

        new_tables = transform_tables(tables, budget_code)

        export_tables(output_directory, new_tables)


    # def _transform(self):
    #     # LOGGER.info(self._parameters['data'])

    #     table_data = self._csv_to_dataframe(self._parameters['data'])
    #     LOGGER.info(f'Post csv to dataframes memory {(hpy().heap())}')

    #     preprocessed_data = self._preprocess_data(table_data)
    #     LOGGER.info(f'Post processed dataframes memory {(hpy().heap())}')

    #     selected_data = self._select_columns(preprocessed_data)
    #     renamed_data = self._rename_columns(selected_data)

    #     postprocessed_data = self._postprocess_data(renamed_data)

    #     return [self._dataframe_to_csv(data) for data in postprocessed_data]

    @classmethod
    def _csv_to_dataframe(cls, data):
        st()
        return [pandas.read_csv(BytesIO(file)) for file in data]
