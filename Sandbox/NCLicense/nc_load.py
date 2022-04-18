import pandas as pd
import settings
import os
from datetime import date
import logging

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

def find_all_scraped_data():
    out_dir = os.environ.get('LICENSE_DIR')
    this_month = date.today().strftime("%Y-%m")
    file_list = []
    for file in os.listdir(out_dir):
        if file.startswith(f"NC_License_Status_{this_month}"):
            file_list.append(f'{out_dir}{file}')
    return file_list

def concat_scraped_data(file_list):
    df_list = []
    for file in file_list:
        df_list.append(pd.read_csv(file))
    all_scraped_data = pd.concat(df_list)
    return all_scraped_data

def confirm_completeness(all_scraped_data):
    today = str(date.today())
    out_dir = os.environ.get('LICENSE_DIR')
    og_file = pd.read_csv(f'{out_dir}NC_{today}.csv')
    missing = og_file[og_file.License_Number.isin(all_scraped_data.License_Number)==False]
    if len(missing)>0:
        status = False
    else:
        status = True
    return status

def create_file():
    today = str(date.today())
    this_month = date.today().strftime("%B")
    file_list = find_all_scraped_data()
    all_scraped_data = concat_scraped_data(file_list)
    local_out = os.environ.get('LICENSE_DIR')
    u_out = os.environ.get('RAW_LICENSE_DIR')
    local_file = f'{local_out}NC_License_Status_{today}.csv'
    u_file = f'{u_out}{this_month}/License/North Carolina/MD Active Type Fixed.txt'
    if confirm_completeness(all_scraped_data):
        og_file = pd.read_csv(f'{local_out}NC_{today}.csv')
        data = pd.merge(og_file, all_scraped_data, suffixes = ['OLD',''])
        data[og_file.columns].to_csv(u_file, sep = '\t', index=False)
        data[og_file.columns].to_csv(local_file, index=False)
    else:
        LOGGER.error('Scraping was incomplete')

if __name__ == "__main__":
    create_file()
