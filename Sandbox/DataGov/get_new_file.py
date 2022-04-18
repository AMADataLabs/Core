import pandas as pd
import os
from datetime import datetime
from enum import Enum
import logging
import time
import settings
from datalabs.access.edw import EDW
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.common.by import By


logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

class Path(Enum):
    URL = 'https://data.cms.gov/provider-data/dataset/mj5m-pzi6'
    PHONE_URL = 'https://data.cms.gov/provider-data/dataset/phys-phon'
    DRIVER = os.environ.get('DRIVER_PATH')
    DOWNLOADS = os.environ.get('DOWNLOAD_FOLDER')
    DATAGOV = os.environ.get('OUT_DIR')
    GOV_TEXT = 'DAC_NationalDownloadableFile'

def wait(browser):
    return WebDriverWait(browser, 30)

def append_me(new_download):
    LOGGER.info('Appending ME numbers')
    with EDW() as edw:
        me_npi = edw.get_me_npi_map()
    new_download['NPI_NBR'] = [str(int(x)) for x in new_download.NPI]
    with_mes = pd.merge(new_download, me_npi, on='NPI_NBR', how='left')
    with_mes.drop(columns = ['NPI_NBR'])
    return with_mes

def get_newest(path):
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files if Path.GOV_TEXT.value in basename]
    return max(paths, key=os.path.getctime)

def get_previous_release_date():
    previous_file = get_newest(Path.DATAGOV.value)
    previous_release = previous_file.split(Path.GOV_TEXT.value)[1].replace('_','').split('.')[0]
    previous_release_date = datetime.strptime(previous_release, '%y%m%d')
    return previous_release_date

def get_current_release_date(driver):
    release_xpath = '//*[@id="root"]/div/div/main/div[2]/div[2]/div[1]/header/div[2]/div[2]'
    current_release_info = wait(driver).until(presence_of_element_located((By.XPATH, release_xpath))).text
    current_release_date = current_release_info.split(': ')[1]
    current_release_date = datetime.strptime(current_release_date, '%b %d, %Y')
    return current_release_date

def is_updated(current_release_date):
    previous_release_date = get_previous_release_date()
    updated = current_release_date > previous_release_date
    return updated
    
def read_and_clean(new_download):
    new_file = pd.read_csv(new_download, encoding='latin')
    new_file.columns = [c.strip() for c in new_file.columns.values]
    new_file = append_me(new_file)
    return new_file

def download_file(driver, current_release_date):
    driver.find_element_by_xpath('//*[@id="dataset-download"]/div/a').click()
    LOGGER.info(f'Downloading...')
    time.sleep(180)
    latest_download = get_newest(Path.DOWNLOADS.value)
    latest_data = read_and_clean(latest_download)
    formatted_date = current_release_date.strftime('%y%m%d')
    latest_filename = f'{Path.DATAGOV.value}_{Path.GOV_TEXT.value}_{formatted_date}.csv'
    latest_data.to_csv(latest_filename, index=False)
    return latest_filename

def get_datagov():
    print(Path.DRIVER.value)
    driver = webdriver.Chrome(executable_path=Path.DRIVER.value)
    driver.get(Path.URL.value)
    current_release_date = get_current_release_date(driver)
    LOGGER.info(f'Data last released {current_release_date}')
    if is_updated(current_release_date):
        LOGGER.info('Data is newer than previous release. Downloading...')
        latest_filename = download_file(driver, current_release_date)
        
    else:
        LOGGER.info('Data has not been updated since previous release.')
        latest_filename = get_newest(Path.DATAGOV.value)
    driver.close()
    return latest_filename

if __name__ == "__main__":
    get_datagov()
