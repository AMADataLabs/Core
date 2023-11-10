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

def practice_completeness(get_new_data):
    path = os.environ.get('LOCAL_OUT')
    today = str(date.today())
    methods_df = connection.get_measurement_methods()
    if get_new_data:
        data_file = practice_data.practice()
    else:
        data_file = connection.get_newest(path,'Practice_Data')
    data = pd.read_csv(data_file, low_memory=False)
    data_dict = data.to_dict('records')
    complete_list = []
    for row in data_dict:
        complete_list += measurement.measure_row(row, methods_df, 'COMPLETENESS')
    practice_completeness = pd.DataFrame(complete_list) 
    practice_filename = f'{path}Practice_Completeness_{today}.csv'
    practice_completeness.to_csv(practice_filename, index=False)

    return practice_completeness

if __name__ == "__main__":
    practice_completeness(get_new_data=False)