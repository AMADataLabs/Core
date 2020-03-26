import datetime

import pandas as pd

from capitalize_column_names import capitalize_column_names

def standardize(data):
    data = capitalize_column_names(data)

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
