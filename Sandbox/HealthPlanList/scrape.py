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

def click_modal_button(browser):
    '''Click button'''
    element = WebDriverWait(browser, 20).until(presence_of_element_located((By.CLASS_NAME, 'modal__button')))
    element.click()

def get_next_page(browser):
    '''Go to next page'''
    WebDriverWait(browser, 20).until(presence_of_element_located((By.XPATH,
                                                                  ('//*[@title="Next Page"]')))).click()
    