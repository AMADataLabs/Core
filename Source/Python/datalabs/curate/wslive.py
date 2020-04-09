""" Utility functions for curating WSLive/Humach survey results data. """
from datetime import datetime
from typing import Iterable

import pandas as pd

import datalabs.curate.dataframe as df


def standardize(data):
    data = df.rename_in_upper_case(data)

    data = _masterfile_sourced_records(data)

    data['WSLIVE_FILE_DT'] = pd.to_datetime(data['WSLIVE_FILE_DT'])

    return data


def most_recent_by_me_number(data):
    data = _sort_by_result_date(data)

    return data.groupby('PHYSICIAN_ME_NUMBER').first().reset_index()


def match_to_sample(data: pd.DataFrame, sample_files: Iterable) -> pd.DataFrame:
    samples = _load_samples(sample_files)

    merged_data = data.merge(samples, how='inner', left_on='PHYSICIAN_ME_NUMBER',  right_on='ME')

    # FIXME: use WS_YEAR as well to properly account for possible "calendar wrap" conditions (i.e. month index cycles back to 1)
    wslive_filter_df = merged_data[merged_data['WS_MONTH'].astype(int) <= merged_data['SAMPLE_MAX_PERFORM_MONTH']]

    wslive_final_df = wslive_filter_df.sort_values('WSLIVE_FILE_DT', 
                            ascending=False).groupby('PHYSICIAN_ME_NUMBER').first().reset_index()

    return wslive_final_df


def _masterfile_sourced_records(data):
    return data[data['SOURCE'].isin(['C', 'Z', 'CR'])]


def _sort_by_result_date(data):
    return data.sort_values(['WSLIVE_FILE_DT'], ascending=False)


def _load_samples(sample_files: Iterable) -> pd.DataFrame:
    samples = []

    for sample_file in sample_files:
        sample = _load_sample(sample_file)
        
        samples.append(sample)

    return pd.concat(samles, ignore_index=True)


def _load_sample(sample_file: str) -> pd.DataFrame:
    sample_date = _extract_sample_date_from_file_name(sample_file)

    sample = pd.read_excel(sample_file, index_col=None, header=0, dtype=str)

    sample = _standardize_sample(sample)

    return sample


def _extract_sample_date_from_file_name(sample_files):
    slash_ndx = [i for i in range(len(sample_file)) if sample_file.startswith('/', i)]
    base_name = sample_file[slash_ndx[-1] + 1:]
    under_ndx = base_name.find('_')
    dash_ndx = base_name.find('-')
    date_str = base_name[dash_ndx + 1:under_ndx]

    return datetime.strptime(date_str, '%Y-%m-%d')


def _standardize_sample(sample: pd.DataFrame, sample_date: datetime) -> pd.DataFrame:
    sample = df.rename_in_upper_case(sample)

    sample['SAMPLE_DATE'] = sample_date
    sample['SAMPLE_SENT_MONTH'] = sample_date.month
    sample['SAMPLE_MAX_PERFORM_MONTH'] = sample_date.month + 2
    sample['SAMPLE_DATE'] = sample_date

    return sample
