import pandas as pd
import settings
import os
from datetime import date
import win32com.client as win32
import errno
import logging

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

def get_raw_filename():
    this_month = date.today().strftime("%B")
    LOGGER.info(f' Licenses from {this_month}')
    folder = os.environ.get('RAW_LICENSE_DIR')
    raw_filename = f'{folder}{this_month}/License/North Carolina/MD-DO-Active-08-03-2023-NCMB.xlsx'
    return raw_filename

def send_email(attachment, auto_send=True):
    outlook = win32.Dispatch('outlook.application')
    msg = outlook.CreateItem(0)
    msg.To = 'victoria.grose@gmail.com'
    msg.Cc = 'victoria.grose@ama-assn.org'
    msg.Subject = 'NC Licenses'
    msg.Body = 'Here you go'
    msg.Attachments.Add(attachment)
    if auto_send:
        msg.Send()
    else:
        msg.Display(True)

def get_license_numbers():
    today = str(date.today())
    raw_filename = get_raw_filename()
    LOGGER.info(f' Reading from U Drive...')
    raw_data = pd.read_excel(raw_filename)
    lic_folder = os.environ.get('LICENSE_DIR')
    lic_filename = f'{lic_folder}NC_FULL_FILE_NUM_ONLY_{today}.csv'
    lic_filename_2 = f'{lic_folder}NC_{today}.csv'
    LOGGER.info(f' Saving locally...')
    raw_data[['License_Number']].to_csv(lic_filename, index=False)
    raw_data.to_csv(lic_filename_2, index=False)
    send_email(lic_filename)
    return lic_filename

if __name__ == "__main__":
    get_license_numbers()