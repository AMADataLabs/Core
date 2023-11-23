import settings
import measurement
import education_data
import connection
import pandas as pd
import os
import logging
from datetime import date

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

def education_completeness(get_new_data):
    path = os.environ.get('LOCAL_OUT')
    today = str(date.today())
    methods_df = connection.get_measurement_methods()
    if get_new_data:
        data_file = education_data.education()
    else:
        data_file = connection.get_newest(path,'Education_Data')
    data = pd.read_csv(data_file, low_memory=False)

    methods = measurement.get_methods(methods_df, 'COMPLETENESS','Education')
    education_completeness = measurement.measure_completeness(methods, data)

    education_filename = f'{path}Education_Completeness_{today}.csv'
    education_completeness.to_csv(education_filename, index=False)

    return education_completeness

if __name__ == "__main__":
    education_completeness(get_new_data=False)