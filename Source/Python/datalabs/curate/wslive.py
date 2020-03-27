""" Utility functions for curating WSLive/Humach survey results data. """

import pandas as pd

import datalabs.curate.dataframe as df

def standardize(data):
    data = df.rename_in_upper_case(data)

    data = masterfile_sourced_records(data)

    data['WSLIVE_FILE_DT'] = pd.to_datetime(data['WSLIVE_FILE_DT'])

    return data

def masterfile_sourced_records(data):
    return data[data['SOURCE'].isin(['C', 'Z', 'CR'])]

def most_recent_by_me_number(data):
    data = sort_by_result_date(data)

    return data.groupby('PHYSICIAN_ME_NUMBER').first().reset_index()

def sort_by_result_date(data):
    return data.sort_values(['WSLIVE_FILE_DT'], ascending=False)
