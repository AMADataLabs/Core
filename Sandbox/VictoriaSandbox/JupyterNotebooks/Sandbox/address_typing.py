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
from selenium.webdriver.common.keys import Keys

def wait(browser):
    '''Define wait'''
    return WebDriverWait(browser, 30)

home_words = ['bed',
'bath',
'zillow',
'redfin',
'realtor',
'bedroom',
'single-family' ,
'home',
'single family',
'house',
'bathrooms',
'trulia',
'condo'
'sq ft'
'apartment',
'renting',
'townhome']

office_words = ['dr.',
'surgery',
'reviews',
'yelp',
'business',
'phone',
'hours',
'physician',
'surgeon',
'clinic',
'main campus',
'doctor',
'website',
'center',
'health',
'surgeries',
'visitor',
'npi',
'acute care',
'hospital']

def get_search_results(ppd_sample, driver):
    dict_list = []
    all_results = []
    for row in ppd_sample.itertuples():
        new_dict = {}
        if row.MAILING_LINE_1 != 'None':
            new_dict['address'] = f'{row.MAILING_LINE_1} {row.MAILING_LINE_2}'
        else:
            new_dict['address'] = row.MAILING_LINE_2
        new_dict['city'] = row.CITY
        new_dict['state'] = row.STATE
        new_dict['address_type'] = row.ADDRESS_TYPE
        new_dict['zipcode'] = str(int(row.ZIP))
        driver.get("http://bing.com")
        search_input = wait(driver).until(presence_of_element_located((By.ID, "sb_form_q")))
        address_input = f"{new_dict['address']} {new_dict['city']} {new_dict['state']} {new_dict['zipcode']}"
        print(address_input)
        search_input.send_keys(address_input)
        search_input.send_keys(Keys.RETURN)
        current_results = driver.find_element_by_id("b_results").text
        all_results.append(current_results)
        new_dict['results'] = current_results
        dict_list.append(new_dict)
        time.sleep(1)
    return(dict_list, all_results)

def address_match(address, results):
    match = 0
    for word in address.split(' '):
        if word in results:
            match += 1
    if match/len(address.split(' ')) > 0.8:
        return True
    else:
        return False
    
def get_address_type(result_dict):
    home_office = 0
    result_list = result_dict['results'].split('...')
    for result in result_list:
        good = False
        office_score = 0
        home_score = 0
        print(result)
        result = result.lower()
        print(result_dict['address'])
        result_dict_address = result_dict['address']
        if 'APT' in result_dict_address:
            result_dict_address = result_dict_address.split('APT')[0]
        if address_match(result_dict_address.lower(),result):
            if result_dict['city'].lower() in result:
                good = True
            elif str(int(result_dict['zipcode'])) in result:
                good = True
        if good == True:
            for word in office_words:
                if word in result:
                    office_score += 1
            for word in home_words:
                if word in result:
                    home_score += 1
            print(office_score)
            print(home_score)
            if office_score > home_score:
                home_office +=1
            elif home_score > office_score:
                home_office -= 1
    return (home_office)

def score_types(dict_list):
    scores = []
    for dicto in dict_list:
        scores.append(get_address_type(dicto))
    return(scores, dict_list)
    
def append_correctness(dict_list, scores):
    shit = pd.DataFrame(dict_list)
    shit['SCORE'] = scores
    corrects = []
    for row in shit.itertuples():
        correct = False
        if row.address_type == 2.0 and row.SCORE < 0:
            correct = True
        elif row.address_type == 1.0 and row.SCORE > 0:
            correct = True
        corrects.append(correct)
    shit['CORRECT']=corrects
    return(shit)

ppd_sample = pd.read_csv('C:/Users/vigrose/Data/PPD/address_sample.csv')
driver_path = 'C:/Users/vigrose/Jupyter Notebooks/chromedriver.exe'
driver = webdriver.Chrome(executable_path=driver_path)
dict_list, all_results = get_search_results(ppd_sample, driver)
driver.close()
scores, dict_list = score_types(dict_list)
final_df = append_correctness(dict_list, scores)

final_df.to_csv('C:/Users/vigrose/Data/PPD/addres_sample_results.csv')