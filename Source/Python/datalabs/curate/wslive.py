""" Utility functions for curating WSLive/Humach survey results data. """
import logging
from typing import Iterable

import pandas as pd

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@pd.api.extensions.register_dataframe_accessor("wslive")
class WSLiveAccessor:
    def __init__(self, data):
        self._data = data

    def match_to_samples(self, samples: pd.DataFrame) -> pd.DataFrame:
        data = self._data.merge(samples, how='inner', left_on='PHYSICIAN_ME_NUMBER', right_on='ME')
        LOGGER.debug('Columns: %s', data.columns.values)
        LOGGER.debug('Merged WSLive data with Samples: %s', data)

        data = self._filter_out_late_results(data)

        return self._most_recent_by_me_number(data)

    def match_to_ppds(self, ppds: pd.DataFrame) -> pd.DataFrame:
        data = self._rename_initial_sample_columns(self._data)
        data = data.merge(ppds, how='inner', left_on='PHYSICIAN_ME_NUMBER', right_on='ME')

        return self._filter_on_ppd_date(data)

    @classmethod
    def _filter_out_late_results(cls, data):
        cls._assert_has_columns(data, ['WSLIVE_FILE_DT', 'SAMPLE_MAX_DATE'])

        return data[data['WSLIVE_FILE_DT'] <= data['SAMPLE_MAX_DATE']]

    @classmethod
    def _most_recent_by_me_number(cls, data):
        data = data.sort_values(['WSLIVE_FILE_DT'], ascending=False)

        return data.groupby('PHYSICIAN_ME_NUMBER').first().reset_index()

    @classmethod
    def _rename_initial_sample_columns(cls, data):
        initial_sample_columns = [
            'POLO_MAILING_LINE_1', 'POLO_MAILING_LINE_2', 'POLO_CITY', 'POLO_STATE', 'POLO_ZIP', 'TELEPHONE_NUMBER',
            'FAX_NUMBER', 'SAMPLE_MAX_DATE', 'SAMPLE_SENT_MONTH', 'SAMPLE_DATE'
        ]
        column_map = {c:'INIT_'+c for c in initial_sample_columns}

        cls._assert_has_columns(data, initial_sample_columns)

        return data.rename(columns=column_map)

    @classmethod
    def _filter_on_ppd_date(cls, data):
        return data[
            (data['INIT_SAMPLE_DATE'].apply(lambda d: d.year) == data['PPD_DATE'].apply(lambda d: d.year)) &
            (data['INIT_SAMPLE_DATE'].apply(lambda d: d.month) == data['PPD_DATE'].apply(lambda d: d.month))
        ]

    @classmethod
    def _assert_has_columns(cls, data: pd.DataFrame, columns: Iterable):
        column_logical_indices = pd.Series([c in data.columns.values for c in columns])
        missing_column_logical_indices = ~column_logical_indices

        if any(missing_column_logical_indices):
            raise AttributeError('The following columns were not found in the WSLive data: {}'.format(
                pd.Series(columns)[missing_column_logical_indices].to_list()
            ))
