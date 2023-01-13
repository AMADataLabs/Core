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

def get_to_login(driver):
    path = '/html/body/table/tbody/tr/td/table[3]/tbody/tr/td[3]/table[2]/tbody/tr/td/table/tbody/tr/td[1]/table/tbody/tr[2]/td/table/tbody/tr/td/div/a'
    login_button = wait(driver).until(presence_of_element_located((By.XPATH, path)))
    login_button.click()
    return driver

def log_in(driver, login, password):
    '''Login to portal'''
    login_input = wait(driver).until(presence_of_element_located((By.ID, "mat-input-2")))
    login_input.send_keys(login)
    password_input = driver.find_element(By.ID, "password-field")
    password_input.send_keys(password)
    login_button = driver.find_element(By.ID, "login-btn")
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
    select_class_level = Select(driver.find_element(By.NAME, 'class_level_cd'))
    select_class_level.select_by_visible_text('All Class Levels')
    for checkbox in driver.find_elements(By.NAME, "displayBioInfo"):
        checkbox.click()
    for checkbox in driver.find_elements(By.NAME,"displayPreviousStatuses"):
        checkbox.click()
    for checkbox in driver.find_elements(By.NAME, "displayCurrentStatuses"):
        checkbox.click()
    return driver

def get_school_select(driver):
    school_dropdown = wait(driver).until(presence_of_element_located((By.NAME, 'med_sch_cd')))
    school_select = Select(school_dropdown)
    return school_select

def get_options(school_select):
    options = school_select.options
    school_options = []
    for option in options:
        school_options.append(option.text)
    return school_options

def iterate_schools(driver):
    '''Download report for each available school'''
    school_select = get_school_select(driver)
    school_options = get_options(school_select)
    schools = school_options.copy()
    for option in school_options[1:]:
        # schools.append(option)
        try:
            school_select.select_by_visible_text(option)
        except:
            error_index = school_options.index(option)-1
            LOGGER.info(f'SRS ERROR: {school_options[error_index]} failed to dowload')
            schools.pop(error_index)
            driver.back()
            time.sleep(2)
            school_select = get_school_select(driver)
            school_select.select_by_visible_text(option)
            continue
        text_xpath = "/html/body/form/table/tbody/tr[8]/td/table/tbody/tr[1]/td[2]/input[3]"
        to_text = driver.find_element(By.XPATH, text_xpath)
        to_text.click()
        submit = driver.find_element(By.NAME, 'submitBtn')
        submit.click()
        LOGGER.info(f'{option} downloading...')
        time.sleep(5)
    driver.quit()
    schools.pop(0)
    # schools = ['Alabama-Heersink 101',
    #             'Albany 102',
    #             'Arizona 193',
    #             'Arizona Phoenix 851',
    #             'Arkansas 103',
    #             'Baylor 104',
    #             'Boston 105',
    #             'Brown-Alpert 192',
    #             'Buffalo-Jacobs 107',
    #             'CUNY 834',
    #             'California 871',
    #             'California Northstate 857',
    #             'Caribe 830',
    #             'Carle Illinois 862',
    #             'Case Western Reserve 186',
    #             'Central Michigan 847',
    #             'Chicago Med Franklin 110',
    #             'Chicago-Pritzker 111',
    #             'Cincinnati 112',
    #             'Colorado 113',
    #             'Columbia-Vagelos 114',
    #             'Connecticut 190',
    #             'Cooper Rowan 848',
    #             'Cornell-Weill 115',
    #             'Creighton 116',
    #             'Dartmouth-Geisel 118',
    #             'Drexel 833',
    #             'Duke 119',
    #             'East Carolina-Brody 813',
    #             'East Tennessee-Quillen 826',
    #             'Eastern Virginia 818',
    #             'Einstein 120',
    #             'Emory 121',
    #             'FIU-Wertheim 837',
    #             'Florida 117',
    #             'Florida Atlantic-Schmidt 854',
    #             'Florida State 811',
    #             'Geisinger Commonwealth 846',
    #             'George Washington 123',
    #             'Georgetown 122',
    #             'Hackensack Meridian 866',
    #             'Harvard 126',
    #             'Hawaii-Burns 197',
    #             'Houston 873',
    #             'Howard 127',
    #             'Illinois 128',
    #             'Indiana 129',
    #             'Iowa-Carver 131',
    #             'Jefferson-Kimmel 132',
    #             'Johns Hopkins 133',
    #             'Kaiser Permanente-Tyson 863',
    #             'Kansas 134',
    #             'Kentucky 135',
    #             'LSU New Orleans 137',
    #             'LSU Shreveport 804',
    #             'Loma Linda 143',
    #             'Louisville 138',
    #             'Loyola-Stritch 139',
    #             'MC Georgia Augusta 124',
    #             'MC Wisconsin 141',
    #             'MU South Carolina 165',
    #             'Marshall-Edwards 828',
    #             'Maryland 142',
    #             'Massachusetts-Chan 195',
    #             'Mayo-Alix 817',
    #             'Meharry 144',
    #             'Mercer 832',
    #             'Miami-Miller 140',
    #             'Michigan 145',
    #             'Michigan State 196',
    #             'Minnesota 146',
    #             'Minnesota Duluth 815',
    #             'Mississippi 147',
    #             'Missouri Columbia 148',
    #             'Missouri Kansas City 808',
    #             'Morehouse 825',
    #             'Mount Sinai-Icahn 801',
    #             'NYU Long Island 872',
    #             'NYU-Grossman 152',
    #             'Nebraska 149',
    #             'Nevada Reno 807',
    #             'New Mexico 150',
    #             'New York Medical 151',
    #             'North Carolina 153',
    #             'North Dakota 154',
    #             'Northeast Ohio 824',
    #             'Northwestern-Feinberg 155',
    #             'Nova Southeastern-Patel 870',
    #             'Oakland Beaumont 844',
    #             'Ohio State 156',
    #             'Oklahoma 157',
    #             'Oregon 158',
    #             'Penn State 198',
    #             'Pennsylvania-Perelman 159',
    #             'Pittsburgh 162',
    #             'Ponce 829',
    #             'Puerto Rico 161',
    #             'Quinnipiac-Netter 855',
    #             'Renaissance Stony Brook 805',
    #             'Rochester 163',
    #             'Rush 812',
    #             'Rutgers New Jersey 170',
    #             'Rutgers-RW Johnson 180',
    #             'SUNY Downstate 136',
    #             'SUNY Upstate 171',
    #             'Saint Louis 164',
    #             'San Juan Bautista 835',
    #             'South Alabama 816',
    #             'South Carolina Columbia 820',
    #             'South Carolina Greenville 850',
    #             'South Dakota-Sanford 166',
    #             'Southern Cal-Keck 167',
    #             'Southern Illinois 810',
    #             'Stanford 169',
    #             'TCU UNTHSC 867',
    #             'Temple-Katz 172',
    #             'Tennessee 173',
    #             'Texas A & M 823',
    #             'Texas Tech 814',
    #             'Texas Tech-Foster 839',
    #             'Toledo 803',
    #             'Tufts 175',
    #             'Tulane 176',
    #             'U Washington 183',
    #             'UC Davis 802',
    #             'UC Irvine 130',
    #             'UC Riverside 849',
    #             'UC San Diego 194',
    #             'UC San Francisco 108',
    #             'UCF 836',
    #             'UCLA Drew 831',
    #             'UCLA-Geffen 109',
    #             'UNLV-Kerkorian 865',
    #             'USF-Morsani 806',
    #             'UT Austin-Dell 859',
    #             'UT Houston-McGovern 809',
    #             'UT Medical Branch 174',
    #             'UT Rio Grande Valley 860',
    #             'UT San Antonio-Long 160',
    #             'UT Southwestern 168',
    #             'Uniformed Services-Hebert 821',
    #             'Utah 177',
    #             'Vanderbilt 178',
    #             'Vermont-Larner 179',
    #             'Virginia 181',
    #             'Virginia Commonwealth 182',
    #             'Virginia Tech Carilion 842',
    #             'Wake Forest 106',
    #             'Washington State-Floyd 869',
    #             'Washington U St Louis 184',
    #             'Wayne State 185',
    #             'West Virginia 187',
    #             'Western Michigan-Stryker 852',
    #             'Wisconsin 188',
    #             'Wright State-Boonshoft 819',
    #             'Yale 191',
    #             'Zucker Hofstra Northwell 845']
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
    driver = get_to_login(driver)
    driver = log_in(driver, user_login, user_password)
    driver = go_to_reports(driver)
    driver = set_preferences(driver)
    school_list = iterate_schools(driver)
    with open(f'{out}School_List_{today}.txt', 'w') as outfile:
        json.dump(school_list, outfile)
    # my_file = open(f'{out}/School_List_2021-09-27.txt')
    # content = my_file.read()
    # school_list = content.replace('[','').replace(']','').replace('"', '').split(', ')
    # my_file.close()
    LOGGER.info(download_folder)
    all_schools = concat_school_reports(school_list, download_folder)
    all_schools.to_csv(f'{out}/SRS_Scrape_{today}.csv', index=False)
    return all_schools

if __name__ == "__main__":
    scrape_srs()
