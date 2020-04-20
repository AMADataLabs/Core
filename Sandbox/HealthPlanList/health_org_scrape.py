'''Scrape NCQA Health Orgs'''
import os
from datetime import date
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_all_elements_located
from scrape import get_driver, click_modal_button, get_next_page

def main():
    '''Main'''
    today = str(date.today())
    out_dir = os.environ.get('OUTPUT_DIR')
    driver = get_driver()
    url = os.environ.get('ORG_URL')
    driver.get(url)
    click_modal_button(driver)
    orgs = scrape_health_orgs(driver)
    orgs.to_csv(f'{out_dir}NCQA_Health_Organizations_{today}.csv', index=False)

def scrape_health_orgs(browser):
    '''Scrape health orgs'''
    driver_closed = False
    name_list = []
    program_list = []
    status_list = []
    website_list = []
    address_list = []
    for num in list(range(0, 22)):
        try:
            time.sleep(2)
            names = WebDriverWait(browser, 20).until(presence_of_all_elements_located((By.CLASS_NAME, 'name')))
            programs = WebDriverWait(browser, 20).until(presence_of_all_elements_located((By.CLASS_NAME, 'program')))
            statuses = WebDriverWait(browser, 20).until(presence_of_all_elements_located((By.CLASS_NAME, 'status')))
            for name in names[1:11]:
                name_list.append(name.text)
            for program in programs[1:11]:
                program_list.append(program.text)
            for status in statuses[1:11]:
                status_list.append(status.text)
            #Click on each link on page
            for index in list(range(0, 10)):
                all_links = WebDriverWait(browser, 20).until(presence_of_all_elements_located((By.XPATH, '//*[@ui-sref="otherHealthCare({org: item.id})"]')))
                all_links[index].click()
                time.sleep(1)
                all_content = WebDriverWait(browser, 20).until(presence_of_all_elements_located((By.CLASS_NAME, 'content')))
                if len(all_content) > 2:
                    website = all_content[0].text
                    address = all_content[1].text
                else:
                    website = 'None'
                    address = all_content[0].text
                website_list.append(website)
                address_list.append(address)
                browser.back()
                time.sleep(1)
            get_next_page(browser)
            print(f'{len(name_list)} health organizations counted')
            print(f'{num} pages scraped')
        except (KeyboardInterrupt, SystemExit):
            min_len = min(len(name_list), len(program_list), len(status_list), len(website_list), len(address_list))
            name_list = name_list[:min_len]
            program_list = program_list[:min_len]
            status_list = status_list[:min_len]
            website_list = website_list[:min_len]
            address_list = address_list[:min_len]
            driver_closed = True
            break
    if not driver_closed:
        browser.close()
    results = pd.DataFrame({'Organization_Name':name_list,
                            'Accreditations':program_list,
                            'Status': status_list,
                            'Website':website_list,
                            'Address':address_list})

    return results

if __name__ == '__main__':
    main()
