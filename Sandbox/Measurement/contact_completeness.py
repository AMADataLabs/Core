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

def address_completeness(data_file, methods, path):
    today = str(date.today())
    data = pd.read_csv(data_file, low_memory=False)
    address_completeness = measurement.measure_completeness(methods, data)
    address_filename = f'{path}Contact_Address_Completeness_{today}.csv'
    address_completeness.to_csv(address_filename, index=False)

    return address_completeness

def phone_completeness(data_file, methods, path):
    today = str(date.today())
    data = pd.read_csv(data_file, low_memory=False)
    phone_completeness = measurement.measure_completeness(methods, data)
    phone_filename = f'{path}Contact_Phone_Completeness_{today}.csv'
    phone_completeness.to_csv(phone_filename, index=False)

    return phone_completeness

def fax_completeness(data_file, methods, path):
    today = str(date.today())
    data = pd.read_csv(data_file, low_memory=False)
    fax_completeness = measurement.measure_completeness(methods, data)
    fax_filename = f'{path}Contact_Fax_Completeness_{today}.csv'
    fax_completeness.to_csv(fax_filename, index=False)

    return fax_completeness

def email_completeness(data_file, methods, path):
    today = str(date.today())
    data = pd.read_csv(data_file, low_memory=False)
    email_completeness = measurement.measure_completeness(methods, data)
    email_filename = f'{path}Contact_Email_Completeness_{today}.csv'
    email_completeness.to_csv(email_filename, index=False)

    return email_completeness

def contact_completeness(get_new_data):
    path = os.environ.get('LOCAL_OUT')
    methods_df = connection.get_measurement_methods()
    if get_new_data:
        data_files = contact_data.contact()
    else:
        address_file = connection.get_newest(path,'Contact_Address_Data')
        phone_file = connection.get_newest(path,'Contact_Phone_Data')
        fax_file = connection.get_newest(path,'Contact_Fax_Data')
        email_file = connection.get_newest(path,'Contact_Email_Data')
        data_files = [address_file, phone_file, fax_file, email_file]

    methods = measurement.get_methods(methods_df, 'COMPLETENESS','Contact')
    address_completeness(data_files[0], methods_df, path)
    phone_completeness(data_files[1], methods_df, path)
    fax_completeness(data_files[2], methods_df, path)
    email_completeness(data_files[3], methods_df, path)

        
if __name__ == "__main__":
    contact_completeness(get_new_data=False)
