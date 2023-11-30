import settings
import measurement
import person_data
import connection
import pandas as pd
import os
import logging
from datetime import date

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

def person_validity(get_new_data):
    path = os.environ.get('LOCAL_OUT')
    today = str(date.today())
    methods_df = connection.get_measurement_methods()
    if get_new_data:
        data_file = person_data.person()
    else:
        data_file = connection.get_newest(path,'Person_Data')
    data = pd.read_csv(data_file, low_memory=False)

    methods = measurement.get_methods(methods_df, 'VALIDITY','Person')
    person_validity = measurement.measure_validity(methods, data, path)

    person_filename = f'{path}Person_Validity{today}.csv'
    person_validity.to_csv(person_filename, index=False)

    return person_validity

if __name__ == "__main__":
    person_validity(get_new_data=False)