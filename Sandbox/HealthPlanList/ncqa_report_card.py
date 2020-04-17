from selenium import webdriver
import pandas as pd
import time

driver = webdriver.Chrome(executable_path='C:/Users/vigrose/hsg-data-labs/Sandbox/HealthPlanList/chromedriver.exe')
driver.get('https://reportcards.ncqa.org/#/health-plans/list')
element = driver.find_element_by_class_name('modal__button')
element.click()
plan_list = []
accr_list = []
state_list = []
insure_list = []
product_list = []

index=0

while index <5:
    names = driver.find_elements_by_class_name('name')
    accrs = driver.find_elements_by_class_name('accr')
    states = driver.find_elements_by_class_name('state')
    insures = driver.find_elements_by_class_name('insurance-type')
    products = driver.find_elements_by_class_name('product-type')
    for plan in names[1:]:
        plan_list.append(plan.text)
    for accr in accrs[1:]:
        accr_list.append(accr.text.replace('Y ',''))
    for insure in insures[1:]:
        insure_list.append(insure.text)
    for state in states[1:11]:
        state_list.append(state.text)
    for product in products[1:]:
        product_list.append(product.text)
    bind_list = driver.find_elements_by_class_name('ng-binding')
    time.sleep(3)
    for bind in bind_list:
        if bind.text=='>':
            bind.click()
            break
    print(f'{len(plan_list)} health plans counted')
    index += 1