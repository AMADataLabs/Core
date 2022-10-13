from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.common.by import By


def get_site(site): 
    driver = webdriver.Chrome(executable_path='C:/Users/vigrose/Jupyter Notebooks/chromedriver.exe')
    driver.get(site)
    return(driver)

