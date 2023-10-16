import pandas as pd
import os
from datetime import date
import datetime as dt
import logging
from dateutil.relativedelta import relativedelta

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

def get_lic_state_creation_dts():
    last_month = (date.today() - relativedelta(months=1)).strftime("%B")
    LOGGER.info(f' Licenses from {last_month}')
    folder = 'U:/Infoverity/Full Source Files - '
    license_folder = f'{folder}{last_month}/License/'
    dict_list = []
    for state in os.listdir(license_folder):
        path = f'{license_folder}{state}'
        x = os.path.getctime(path) 
        creation_date = dt.datetime.fromtimestamp(x)
        new_dict = {
            'STATE': state,
            'CREATION_DT': creation_date
        }
        dict_list.append(new_dict)
    
    return dict_list, last_month

def transform_creation_date_data(dict_list):
    for x in dict_list:
        thing = x['STATE'].split(' ')[-1]
        if thing in ['DO','MD']:
            license_degree = thing
            state = x['STATE'].replace(f' {thing}','')
        else:
            license_degree = ''
            state = x['STATE']
        if thing in ['TR','IR']:
            lic_type = 'Resident'
            state = x['STATE'].replace(f' {thing}','')
        else:
            lic_type = ''
        x['LICENSE_TYPE'] = lic_type
        x['LICENSE_DEGREE'] = license_degree
        x['LIC_STATE'] = state
    return dict_list

def license_times():
    dict_list, last_month = get_lic_state_creation_dts()
    dict_list = transform_creation_date_data(dict_list)
    lic_state_df = pd.DataFrame(dict_list)
    LOGGER.info(f' Saving...')
    lic_state_df.to_csv(f'C:/Users/vigrose/Data/Measurement/License_Folder_Creation_{last_month}.csv', index=False)

if __name__ == "__main__":
    license_times()


