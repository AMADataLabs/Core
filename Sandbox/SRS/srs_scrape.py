'''Scrape change of status reports from student portal'''
import time
import os
from datetime import date, datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import json
import settings
import logging
import useful_functions as use
from selenium.common.exceptions import NoSuchElementException
import warnings

warnings.simplefilter("ignore")

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

def wait(browser):
    '''Define wait'''
    return WebDriverWait(browser, 30)

def check_exists_by_xpath(xpath):
    try:
        webdriver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True

def get_newest(path, text):
    '''Get newest filename'''
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files if text in basename]
    return max(paths, key=os.path.getctime)

def get_to_login(driver):
    path = '/html/body/table/tbody/tr/td/table[3]/tbody/tr/td[3]/table[2]/tbody/tr/td/table/tbody/tr/td[1]/table/tbody/tr[2]/td/table/tbody/tr/td/div/a'
    login_button = wait(driver).until(presence_of_element_located((By.XPATH, path)))
    login_button.click()
    return driver

def log_in(driver, login, password):
    '''Login to portal'''
    login_input = wait(driver).until(presence_of_element_located((By.NAME, "IDToken1")))
    login_input.send_keys(login)
    password_input = driver.find_element(By.NAME, "IDToken2")
    password_input.send_keys(password)
    login_button = driver.find_element(By.ID, "login-btn")
    time.sleep(2)
    login_button.click()
    return driver

def go_to_reports(driver):
    '''Go to report page'''
    path = '/html/body/srs-root/div/aamc-ui-layout/div/header/aamc-ui-header/mat-toolbar/nav/aamc-ui-header-item[4]/div/a/span[1]/div/span'
    get_reports = wait(driver).until(presence_of_element_located((By.XPATH, path)))
    get_reports.click()
    return driver

def select_role(driver):
    try:
        xpath = '//*[@id="mat-radio-2"]/label/span[1]/span[2]'
        role_selection = wait(driver).until(presence_of_element_located((By.XPATH,xpath)))
        role_selection.click()
    except:
        xpath = '//*[@id="mat-radio-2"]/label/span[1]/span[1]'
        role_selection = wait(driver).until(presence_of_element_located((By.XPATH,xpath)))
        role_selection.click()
    class_test = "mat-primary"
    role_select = wait(driver).until(presence_of_element_located((By.CLASS_NAME,class_test)))
    role_select.click()
    return driver

def set_class_level(driver):
    #get all class levels
    try:
        xpath = '//*[@id="classlevel"]/div/span'
        thing = wait(driver).until(presence_of_element_located((By.XPATH,xpath)))
        thing.click()
    except:
        class_ = 'ng-arrow-wrapper'
        dropdown = wait(driver).until(presence_of_element_located((By.CLASS_NAME,class_)))
        dropdown.click()
    time.sleep(0.5)
    class_ = "ng-star-inserted"    
    parameter_options = driver.find_elements(By.CLASS_NAME,class_)
    for option in parameter_options:
        if option.text == 'All Class Levels':
            option.click()
            break
    time.sleep(0.5)
    return driver

def set_preferences(driver):
    '''Check all report preferences'''
    #get all dropdowns and click program dropdown
    class_ = 'ng-arrow-wrapper'
    dropdowns = driver.find_elements(By.CLASS_NAME,class_)
    dropdowns[2].click()
    time.sleep(0.5)
    #click all programs?
    class_ = "ng-star-inserted"
    parameter_options = driver.find_elements(By.CLASS_NAME,class_)
    for option in parameter_options:
        if option.text == 'ALL':
            option.click()
            break
    time.sleep(0.5)
    #select current statuses
    class_ = 'ng-arrow-wrapper'
    dropdowns = driver.find_elements(By.CLASS_NAME,class_)
    dropdowns[3].click()
    class_ = "ng-star-inserted"
    parameter_options = driver.find_elements(By.CLASS_NAME,class_)
    for option in parameter_options:
        if option.text == 'All Statuses':
            option.click()
            break
    #SELECT ALL DISPLAY FIELDS
    class_ = "hand"
    select_options = driver.find_elements(By.CLASS_NAME,class_)
    for option in select_options:
        if option.text == 'SELECT ALL':
            option.click()
    time.sleep(0.5)
    return driver

def get_school_dropdown(driver):
    # path = '//*[@id="mat-dialog-1"]/aamc-ui-modal/div/div/mda-srs-common-components-select-school/div/form/div[1]/aamc-ui-extended-field/div[1]/label/ng-select/div/span'
    class_ = 'ng-arrow-wrapper'
    school_dropdown = wait(driver).until(presence_of_element_located((By.CLASS_NAME,class_)))
    school_dropdown.click()
    return driver

def get_school_options(driver):
    class_ = "ng-option"
    schools = driver.find_elements(By.CLASS_NAME,class_)
    school_list = []
    for school in schools:
        school_list.append(school.text)
    return driver, school_list

def get_select_locale(driver):
    for num in len(range(0,9)):
        potential_xpath = f'//*[@id="mat-dialog-{num}"]/aamc-ui-modal/div/div/mda-srs-common-components-select-school/div/form/div[2]/button[2]/span[1]'
        if check_exists_by_xpath(potential_xpath):
            return potential_xpath

def select_school(driver, school_name):
    #pick new school
    xpath = '/html/body/div[1]/div[2]/div/mat-dialog-container/aamc-ui-modal/div/div/mda-srs-common-components-select-school/div/form/div[1]/aamc-ui-extended-field/div[1]/label/ng-select/div/span[2]'
    school_dropdown = wait(driver).until(presence_of_element_located((By.XPATH,xpath)))
    school_dropdown.click()
    #select next school
    class_ = "ng-option"
    schools = driver.find_elements(By.CLASS_NAME,class_)
    for school in schools:
        if school.text == school_name:
            school.click()
            break
    #get new school
    try:
        xpath = '//*[@id="mat-dialog-2"]/aamc-ui-modal/div/div/mda-srs-common-components-select-school/div/form/div[2]/button[2]/span[1]'
        school_select = driver.find_element(By.XPATH,xpath)
        school_select.click()
    except:
        xpath = '//*[@id="mat-dialog-0"]/aamc-ui-modal/div/div/mda-srs-common-components-select-school/div/form/div[2]/button[2]/span[1]'
        school_select = driver.find_element(By.XPATH,xpath)
        school_select.click()
    return driver

def download_report(driver):
    #get report
    get_report_class = "mat-primary"
    get_report = wait(driver).until(presence_of_element_located((By.CLASS_NAME,get_report_class)))
    get_report.click()
    #wait
    LOGGER.info(f'Generating report...')
    # time.sleep(30)
    #download
    xpath = '//*[@id="main-content"]/mda-srs-reports-custom-reports/div/div/mat-card/mat-card-content/div[2]/aamc-ui-page-header/mat-toolbar/button/span[1]'
    time.sleep(30)
    download = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH,xpath)))
    download.click()
    LOGGER.info(f'Starting download...')
    time.sleep(30)
    return driver

def change_school(driver):
    xpath = '//*[@id="main-content"]/router-outlet/mda-srs-common-components-breadcrumb-school-view/div/div/div[2]/span'
    change_school = wait(driver).until(presence_of_element_located((By.XPATH,xpath)))
    change_school.click()
    return driver

def first_round(driver, school_1):
    #first school
    class_ = "ng-option"
    schools = driver.find_elements(By.CLASS_NAME,class_)
    for school in schools:
        if school.text == school_1:
            school.click()
            break
    class_test = "mat-primary"
    role_select = wait(driver).until(presence_of_element_located((By.CLASS_NAME,class_test)))
    role_select.click()
    #go to custom report
    xpath = '//*[@id="main-content"]/mda-srs-reports-home/div/div/mat-card/ol/li[2]/p/a'
    get_custom_reports = wait(driver).until(presence_of_element_located((By.XPATH,xpath)))
    get_custom_reports.click()
    time.sleep(2)
    try:
        driver = set_class_level(driver)
        driver = set_preferences(driver)
        LOGGER.info(f'{school_1} downloading...')
        driver = download_report(driver)
    except:
        driver.refresh()
        driver = set_class_level(driver)
        driver = set_preferences(driver)
        LOGGER.info(f'{school_1} downloading...')
        driver = download_report(driver)
    return driver

def iterate_schools(driver, school_list):
    '''Download report for each available school'''
    for school_name in school_list:
        LOGGER.info(f'Starting {school_name}...')
        driver = change_school(driver)
        time.sleep(1)
        driver = select_school(driver, school_name)
        time.sleep(2)
        try:
            driver = set_class_level(driver)
            driver = set_preferences(driver)
            LOGGER.info(f'{school_name} downloading...')
            driver = download_report(driver)
        except:
            driver = driver.refresh()
            time.sleep(2)
            driver = set_class_level(driver)
            driver = set_preferences(driver)
            LOGGER.info(f'{school_name} downloading...')
            driver = download_report(driver)
        time.sleep(5)
    driver.quit()
    return driver

def concat_school_reports(download_folder):
    '''Find all downloads and merge'''
    today = datetime.today().date()
    files = os.listdir(download_folder)
    text = 'CustomReport'
    paths = [os.path.join(download_folder, basename) for basename in files if text in basename]
    all_data = pd.DataFrame()
    for file in paths:
        c_timestamp = os.path.getctime(file)
        c_datestamp = datetime.fromtimestamp(c_timestamp)
        if c_datestamp.date() == today:
            new_df = pd.read_excel(file, engine="openpyxl")
            all_data = pd.concat([all_data, new_df])
    all_data = all_data.drop_duplicates()
    return all_data

def scrape_srs():
    '''Download all schools SRS reports from portal and create file'''
    today = str(date.today())
    out = os.environ.get('OUT_DIR')
    url = os.environ.get('URL')
    user_login = os.environ.get('LOGIN')
    # print(user_login)
    user_password = os.environ.get('PASSWORD')
    # print(user_password)
    download_folder = os.environ.get('DOWNLOAD_FOLDER')
    driver_path = os.environ.get('DRIVER_PATH')
    driver = webdriver.Chrome(executable_path=driver_path)
    time.sleep(2)
    driver.get(url)
    time.sleep(3)
    # driver = get_to_login(driver)
    LOGGER.info(f'Logging in...')
    driver = log_in(driver, user_login, user_password)
    time.sleep(5)
    LOGGER.info(f'Selecting role...')
    driver = select_role(driver)
    time.sleep(5)
    LOGGER.info(f'Going to reports...')
    driver = go_to_reports(driver)
    time.sleep(5)
    LOGGER.info(f'Getting all schools...')
    driver = get_school_dropdown(driver)
    driver, school_list = get_school_options(driver)
    LOGGER.info(f'Getting first school...')
    driver = first_round(driver, school_list)
    LOGGER.info(f'Iterating schools...')
    try:
        driver = iterate_schools(driver, school_list[1:])
    except:
        driver = iterate_schools(driver, school_list[1:])
    # my_file = open(f'{out}/School_List_2021-09-27.txt')
    # content = my_file.read()
    # school_list = content.replace('[','').replace(']','').replace('"', '').split(', ')
    # my_file.close()
    LOGGER.info(download_folder)
    all_schools = concat_school_reports(download_folder)
    all_schools.to_csv(f'{out}/SRS_Scrape_{today}.csv', index=False)
    return all_schools

if __name__ == "__main__":
    scrape_srs()
