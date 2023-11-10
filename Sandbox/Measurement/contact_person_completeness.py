import settings
import measurement
import contact_data
import connection
import pandas as pd
import os
import logging
from datetime import date

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

def contact_person_completeness(get_new_data):
    path = os.environ.get('LOCAL_OUT')
    today = str(date.today())
    methods_df = connection.get_measurement_methods()
    if get_new_data:
        data_file = contact_data.contact()
    else:
        data_file = connection.get_newest(path,'Contact_Party_Level_Data')
    data = pd.read_csv(data_file, low_memory=False)

    methods = measurement.get_methods(methods_df, 'COMPLETENESS','Contact')
    contact_completeness = measurement.measure_completeness(methods, data)

    contact_filename = f'{path}Contact_Party_Level_Completeness_{today}.csv'
    contact_completeness.to_csv(contact_filename, index=False)

    return contact_completeness

if __name__ == "__main__":
    contact_person_completeness(get_new_data=False)