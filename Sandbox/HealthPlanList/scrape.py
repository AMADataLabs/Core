'''Define common scraping functions'''
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
import settings

def get_driver():
    '''Get webdriver'''
    driver_loc = os.environ.get('DRIVER_PATH')
    browser = webdriver.Chrome(executable_path=driver_loc)
    return browser

def wait(browser):
    '''Define wait'''
    return WebDriverWait(browser, 30)

def click_modal_button(browser):
    '''Click button'''
    element = wait(browser).until(presence_of_element_located((By.CLASS_NAME, 'modal__button')))
    element.click()

def get_next_page(browser):
    '''Go to next page'''
    next_path = '//*[@title="Next Page"]'
    wait(browser).until(presence_of_element_located((By.XPATH, next_path))).click()

def get_min(list_o_lists):
    '''Get len of shortest list'''
    lens = []
    for thing in list_o_lists:
        lens.append(len(thing))
    minimum = min(lens)
    return minimum
