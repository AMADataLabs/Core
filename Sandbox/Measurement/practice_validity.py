import settings
import measurement
import practice_data
import connection
import pandas as pd
import os
import logging
from datetime import date

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

def practice_validity(get_new_data):
    path = os.environ.get('LOCAL_OUT')
    today = str(date.today())
    methods_df = connection.get_measurement_methods()
    if get_new_data:
        data_file = practice_data.practice()
    else:
        data_file = connection.get_newest(path,'Practice_Data')
    data = pd.read_csv(data_file, low_memory=False)

    methods = measurement.get_methods(methods_df, 'VALIDITY','Practice')
    practice_validity = measurement.measure_validity(methods, data, path)

    practice_filename = f'{path}Practice_Validity{today}.csv'
    practice_validity.to_csv(practice_filename, index=False)

    return practice_validity

if __name__ == "__main__":
    practice_validity(get_new_data=False)