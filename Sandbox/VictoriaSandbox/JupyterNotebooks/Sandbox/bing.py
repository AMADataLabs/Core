import time
import os
from datetime import date
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import pandas as pd
import json

def wait(browser):
    '''Define wait'''
    return WebDriverWait(browser, 30)

def bing_search(search_input):
    today = str(date.today())
    out = "C:/Users/vigrose/Data/PhoneAppend/"
    url = "http://bing.com"
    driver_path = 'C:/Users/vigrose/Jupyter Notebooks/chromedriver.exe'
    driver = webdriver.Chrome(executable_path=driver_path)
    time.sleep(1)
    driver.get(url)
    search_box = wait(driver).until(presence_of_element_located((By.ID, "sb_form_q")))
    print(search_input)
    search_box.send_keys(search_input)
    search_box.send_keys(Keys.RETURN)
    current_results = driver.find_element_by_id("b_results").text
    result_list = current_results.split('...')
    with open(f'{out}Bing_Results_{today}.txt', 'w') as outfile:
        json.dump(current_results, outfile)
    return (driver, result_list)

def get_infos(driver, row):
    name = row.MAILING_NAME
    og_url = driver.current_url
    maxi = len(driver.find_elements_by_tag_name("h2"))
    dict_list = []
    for link in range(0,maxi):
        try:
            wait(driver).until(presence_of_element_located((By.TAG_NAME, "h2")))
            try:
                print(driver.find_elements_by_tag_name("h2")[link].text)
                driver.find_elements_by_tag_name("h2")[link].click()
            except:
                continue
#             driver.current_url!=og_url:
            test = driver.find_element_by_tag_name('body').text
            new_test = test.replace(' ','').replace(')','').replace('(','').replace('-','')
            url = driver.current_url
            for x in range(len(new_test)):
                potential_number = new_test[x:x+10]
                if potential_number.isnumeric():
                    if potential_number[0]=='1':
                        potential_number = new_test[x:x+11]
                    print(potential_number)
                    new_dict = {
                            'NAME': name,
                            'URL':driver.current_url,
                            'NUMBERS': potential_number
                        }
                    dict_list.append(new_dict)
            if driver.current_url!=og_url:
                driver.back()
        except:
            break
#         driver.find_element_by_class_name("sb_pagN").click()
    return (driver, dict_list)

def search_and_find(row, driver):
    driver.get('http://bing.com')
    search_input = wait(driver).until(presence_of_element_located((By.ID, "sb_form_q")))
    if row.ADDR_2 == 'None':
        addr_2 = ''
    else:
        addr_2 = row.OFFICE_ADDRESS_LINE_1 + ' '
    if row.ADDR_3 == 'None':
        addr_3 = ''
    else:
        addr_3 = row.ADDR_1 + ' '
    address_input = f'{row.MAILING_NAME} {row.ADDR_1}{addr_2}{addr_3} {row.CITY} {row.STATE} {row.ZIP}'
    search_input.send_keys(address_input)
    search_input.send_keys(Keys.RETURN)
    driver, dict_list = get_infos (driver, row)
    return (driver, dict_list)

def clean_file(result_list):
    this =[]
    for thing in result_list:
        for thing_2 in thing:
            this.append(thing_2)
    address_results = pd.DataFrame(this)
    return(address_results)

def bing_phone_append():
    sample = pd.read_csv('sample')
            
    new_count = 0
    address_list = [] 

    for row in sample[new_count:].itertuples():
        driver, new_list = search_and_find(row, driver)
        address_list.append(new_list)
        new_count+=1
        print(f'{round((new_count/5000*100),2)}% done')

    clean_file(address_list)

# if __name__ == "__main__":
#     scrape_srs()