from selenium import webdriver
import pandas as pd
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.common.by import By
from datetime import datetime, date
import logging
import os
import settings

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

def wait(browser):
    '''Define wait'''
    return WebDriverWait(browser, 30)

def get_license_info(license_number, driver):
    time.sleep(1)
    license_input = wait(driver).until(presence_of_element_located((By.ID, "txtLicNum")))
    license_input.clear()
    license_input.send_keys(license_number)
    submit = driver.find_element_by_id("btnSubmit")
    submit.click()
    try:
        table =  wait(driver).until(presence_of_element_located((By.TAG_NAME,'tbody')))
        info_link = table.find_elements_by_tag_name('a')
        if info_link:
            info_link[0].click()
            license_statuses = driver.find_elements_by_xpath('//*[@id="pnlVerificationBody"]/div[1]/div[1]')
            if license_statuses:
                license_type = license_statuses[0].text.split('- ')[1]
            else:
                license_type = 'None'
        else:
            license_type = 'Not found'
        time.sleep(1)
        new_search = wait(driver).until(presence_of_element_located((By.XPATH,'//*[@id="content"]/div/div[2]/div[3]/a[3]')))
        new_search.click()
    except:
        license_type = 'Not found'
    return(license_type, driver)

def save_it(license_dict_list):
    out_dir = os.environ.get('LICENSE_DIR')
    today_time = str(datetime.today()).replace(':','').replace('.','').replace(' ','_')
    pd.DataFrame(license_dict_list).to_csv(F'{out_dir}NC_License_Status_{today_time}.csv', index=False)

def scrape():
    today = str(date.today())
    lic_dir = os.environ.get('LICENSE_DIR')
    lic_loc = f'{lic_dir}NC_FULL_FILE_NUM_ONLY_{today}.csv'
    LOGGER.info(f'Licenses in {lic_loc}')
    nc_lic = pd.read_csv(lic_loc)
    LOGGER.info('File read')
    license_list = list(nc_lic['License_Number'])
    license_dict_list = []
    index=0
    driver = webdriver.Chrome(executable_path=os.environ.get('DRIVER_PATH'))
    LOGGER.info('Accessing site...')
    driver.get(os.environ.get('URL'))
    try:
        for lic in license_list[index:]:
            license_type, driver = get_license_info(lic, driver)
            license_dict = {
                    'License_Number': lic,
                    'License_Type': license_type

                }
            LOGGER.info(license_dict)
            license_dict_list.append(license_dict)
            index+=1
    except:
        LOGGER.error('Interrupted')
        save_it(license_dict_list)
        nc_lic[index:].to_csv(lic_loc, index=False)
    save_it(license_dict_list)
    driver.quit()

if __name__ == "__main__":
    scrape()



    

