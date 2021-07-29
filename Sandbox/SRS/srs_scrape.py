'''Scrape change of status reports from student portal'''
import time
import os
from datetime import date
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import pandas as pd
import json
import settings
import logging
import useful_functions as use

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

def wait(browser):
    '''Define wait'''
    return WebDriverWait(browser, 30)

def get_newest(path, text):
    '''Get newest filename'''
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files if text in basename]
    return max(paths, key=os.path.getctime)

def log_in(driver, login, password):
    '''Login to portal'''
    login_input = wait(driver).until(presence_of_element_located((By.ID, "mat-input-2")))
    login_input.send_keys(login)
    password_input = driver.find_element_by_id("password-field")
    password_input.send_keys(password)
    login_button = driver.find_element_by_id("login-btn")
    login_button.click()
    return driver

def go_to_reports(driver):
    '''Go to report page'''
    report_xpath = "/html/body/table[2]/tbody/tr[3]/td/table/tbody/tr/td[14]/a"
    custom_xpath = "/html/body/table[3]/tbody/tr[1]/td/table/tbody/tr/td[5]/a"
    get_reports = wait(driver).until(presence_of_element_located((By.XPATH, report_xpath)))
    get_reports.click()
    get_custom_reports = wait(driver).until(presence_of_element_located((By.XPATH, custom_xpath)))
    get_custom_reports.click()
    return driver

def set_preferences(driver):
    '''Check all report preferences'''
    select_class_level = Select(driver.find_element_by_name('class_level_cd'))
    select_class_level.select_by_visible_text('All Class Levels')
    for checkbox in driver.find_elements_by_name("displayBioInfo"):
        checkbox.click()
    for checkbox in driver.find_elements_by_name("displayPreviousStatuses"):
        checkbox.click()
    for checkbox in driver.find_elements_by_name("displayCurrentStatuses"):
        checkbox.click()
    return driver

def iterate_schools(driver):
    '''Download report for each available school'''
    school_dropdown = wait(driver).until(presence_of_element_located((By.NAME, 'med_sch_cd')))
    school_select = Select(school_dropdown)
    options = school_select.options
    schools = []
    for option in options[1:]:
        schools.append(option.text)
        LOGGER.info(f'{option.text} downloading...')
        school_select.select_by_visible_text(option.text)
        text_xpath = "/html/body/form/table/tbody/tr[8]/td/table/tbody/tr[1]/td[2]/input[3]"
        to_text = driver.find_element_by_xpath(text_xpath)
        to_text.click()
        submit = driver.find_element_by_name('submitBtn')
        submit.click()
        time.sleep(5)
    driver.quit()
    return schools

def concat_school_reports(schools, download_folder):
    '''Find all downloads and merge'''
    all_schools = pd.DataFrame()
    for school in schools:
        school_num = school.split(' ')[-1]
        school_name = school.replace(f' {school_num}', '')
        if '/' in school_name:
            school_name = school_name.split('/')[0]
        LOGGER.info(f'{school_name} added')
        filepath = get_newest(download_folder, school_name)
        school_info = pd.read_csv(filepath, sep="|", encoding='unicode_escape')
        school_info['SCHOOL'] = school_name
        all_schools = pd.concat([all_schools, school_info])
    return all_schools

def scrape_srs():
    '''Download all schools SRS reports from portal and create file'''
    today = str(date.today())
    out = os.environ.get('OUT_DIR')
    url = os.environ.get('URL')
    user_login = os.environ.get('LOGIN')
    user_password = os.environ.get('PASSWORD')
    download_folder = os.environ.get('DOWNLOAD_FOLDER')
    driver_path = os.environ.get('DRIVER_PATH')
    driver = webdriver.Chrome(executable_path=driver_path)
    time.sleep(1)
    driver.get(url)
    driver = log_in(driver, user_login, user_password)
    driver = go_to_reports(driver)
    driver = set_preferences(driver)
    school_list = iterate_schools(driver)
    with open(f'{out}School_List_{today}.txt', 'w') as outfile:
        json.dump(school_list, outfile)
    # my_file = open(f'{out}/School_List_2021-06-03.txt')
    # content = my_file.read()
    # school_list = content.replace('[','').replace(']','').replace('"', '').split(', ')
    # my_file.close()
    # print(download_folder)
    all_schools = concat_school_reports(school_list, download_folder)
    all_schools.to_csv(f'{out}/SRS_Scrape_{today}.csv', index=False)
    return all_schools

if __name__ == "__main__":
    scrape_srs()
