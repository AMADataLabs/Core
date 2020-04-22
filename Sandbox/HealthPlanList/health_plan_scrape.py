'''Scrape NCQA health plans'''
import os
from datetime import date
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import presence_of_all_elements_located
from scrape import get_driver, click_modal_button, get_next_page, wait, get_min

def main():
    '''Main'''
    today = str(date.today())
    out_dir = os.environ.get('OUTPUT_DIR')
    driver = get_driver()
    url = os.environ.get('PLAN_URL')
    driver.get(url)
    click_modal_button(driver)
    plans = scrape_health_plans(driver)
    plans.to_csv(f'{out_dir}NCQA_Health_Plans_{today}.csv', index=False)


def scrape_health_plans(browser):
    '''Scrape health orgs'''
    driver_closed = False
    name_list = []
    accr_list = []
    state_list = []
    insure_list = []
    product_list = []
    website_list = []
    members_list = []
    other_names_list = []
    for num in list(range(0, 22)):
        try:
            time.sleep(2)
            names = wait(browser).until(presence_of_all_elements_located((By.CLASS_NAME, 'name')))
            accrs = wait(browser).until(presence_of_all_elements_located((By.CLASS_NAME,
                                                                          'accr')))
            states = wait(browser).until(presence_of_all_elements_located((By.CLASS_NAME,
                                                                           'state')))
            products = wait(browser).until(presence_of_all_elements_located((By.CLASS_NAME,
                                                                             'product-type')))
            insures = wait(browser).until(presence_of_all_elements_located((By.CLASS_NAME,
                                                                            'insurance-type')))
            for name in names[1:11]:
                name_list.append(name.text)
            for accr in accrs[1:11]:
                accr_list.append(accr.text.replace('Y ', ''))
            for insure in insures[1:11]:
                insure_list.append(insure.text)
            for state in states[1:11]:
                state_list.append(state.text)
            for product in products[1:11]:
                product_list.append(product.text)
            #Click on each link on page
            for index in list(range(0, 10)):
                link_path = '//*[@ui-sref="healthPlan({id: item.id})"]'
                all_links = wait(browser).until(presence_of_all_elements_located((By.XPATH,
                                                                                  link_path)))
                all_links[index].click()
                time.sleep(1)
                all_content = wait(browser).until(presence_of_all_elements_located((By.CLASS_NAME,
                                                                                    'content')))
                website = all_content[2].text
                members = all_content[4].text
                other_names = all_content[5].text
                if "Why" in other_names:
                    other_names = 'None'
                website_list.append(website)
                members_list.append(members)
                other_names_list.append(other_names)
                browser.back()
                time.sleep(1)
            get_next_page(browser)
            print(f'{len(name_list)} health plans counted')
            print(f'{num + 1} pages scraped')
        except (KeyboardInterrupt, SystemExit):
            driver_closed = True
            break
    minimum = get_min([name_list,
                       accr_list,
                       state_list,
                       insure_list,
                       product_list,
                       website_list,
                       members_list,
                       other_names_list])
    if not driver_closed:
        browser.close()
    results = pd.DataFrame({'Health_Plan_Type':name_list[0:minimum],
                            'Accreditation':accr_list[0:minimum],
                            'States_Served': state_list[0:minimum],
                            'Insurance_Type': insure_list[0:minimum],
                            'Product_Type':product_list[0:minimum],
                            'Website':website_list[0:minimum],
                            'Members':members_list[0:minimum],
                            'Other_Names': other_names_list[0:minimum]})

    return results

if __name__ == '__main__':
    main()
