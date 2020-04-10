""" Utility functions for curating WSLive/Humach survey results data. """
from datetime import datetime, timedelta
import logging
from typing import Iterable

import pandas as pd

import datalabs.curate.dataframe as df

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@pd.api.extensions.register_dataframe_accessor("wslive")
class WSLiveAccessor:
    def __init__(self, data):
        self._data = data

    def standardize(self):
        data = df.rename_in_upper_case(self._data)

        data = self._filter_for_masterfile_sourced_rows(data)

        data['WSLIVE_FILE_DT'] = pd.to_datetime(data['WSLIVE_FILE_DT'])

        return data

    def most_recent_by_me_number(self):
        data = self._sort_by_result_date(self._data)

        return data.groupby('PHYSICIAN_ME_NUMBER').first().reset_index()

    def match_to_samples(self, samples: pd.DataFrame) -> pd.DataFrame:
        data = self._data.merge(samples, how='inner', left_on='PHYSICIAN_ME_NUMBER',  right_on='ME')
        LOGGER.debug('Columns: %s', data.columns.values)
        LOGGER.debug('Merged WSLive data with Samples: %s', data)

        data = self._filter_out_late_results(data)

        data = self._sort_by_result_date(data)

        return data.groupby('PHYSICIAN_ME_NUMBER').first().reset_index()

    @classmethod
    def _sort_by_result_date(cls, data):
        return data.sort_values(['WSLIVE_FILE_DT'], ascending=False)

    @classmethod
    def _filter_for_masterfile_sourced_rows(cls, data):
        return data[data['SOURCE'].isin(['C', 'Z', 'CR'])]

    @classmethod
    def _filter_out_late_results(cls, data):
        data['WS_DAY'] = 1
        date_data = data[['WS_YEAR', 'WS_MONTH', 'WS_DAY']].rename(
            columns={'WS_YEAR': 'year', 'WS_MONTH': 'month', 'WS_DAY': 'day'}
        )
        data['WS_DATE'] = pd.to_datetime(date_data)

        return data[data['WS_DATE'] <= data['SAMPLE_MAX_DATE']]


class SampleLoader:
    def load_samples(self, sample_files: Iterable) -> pd.DataFrame:
        samples = []

        for sample_file in sample_files:
            sample = self.load_sample(sample_file)
            
            samples.append(sample)

        return pd.concat(samles, ignore_index=True)

    def load_sample(self, sample_file: str) -> pd.DataFrame:
        sample_date = _extract_sample_date_from_file_name(sample_file)

        sample = pd.read_excel(sample_file, index_col=None, header=0, dtype=str)

        sample = self._standardize_sample(sample, sample_date)

        return sample

    def _extract_sample_date_from_file_name(self, sample_files):
        slash_ndx = [i for i in range(len(sample_file)) if sample_file.startswith('/', i)]
        base_name = sample_file[slash_ndx[-1] + 1:]
        under_ndx = base_name.find('_')
        dash_ndx = base_name.find('-')
        date_str = base_name[dash_ndx + 1:under_ndx]

        return datetime.strptime(date_str, '%Y-%m-%d')

    def _standardize_sample(self, sample: pd.DataFrame, sample_date: datetime) -> pd.DataFrame:
        sample = df.rename_in_upper_case(sample)

        sample['SAMPLE_DATE'] = sample_date
        sample['SAMPLE_MAX_DATE'] = sample_date + timedelta(months=2)

        return sample
