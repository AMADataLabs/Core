import json
from datetime import date
import boto3
import pandas as pd
import requests
from bs4 import BeautifulSoup
bucket  = 'pa-data-output-file-csv'
file_name = sample
def scrape():
    NUM_LIST = list(range(1, 474))

    DICT_LIST = []
    TEXT_LIST = []
    for num in NUM_LIST:
        base_url = f'''
        https://www.henryford.com/physician-directory/search-results?page={num}&zip=&specialties=
        '''
        response = requests.get(base_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        TEXT_LIST.append(soup.text)
        listings = soup.find_all(class_='listing')
        for listing in listings:
            link = listing.find('a')['href']
            try:
                phone = listing.find(class_='phones').text
            except:
                phone = 'None'
            try:
                specialty = listing.find(class_='module-pd-specialty-list').text
                specialty = specialty.replace('\n', '').replace('Specialties: ', '')
            except:
                specialty = 'None'
            try:
                name = listing.find('img')['alt']
            except:
                name = 'None'
            print(f"{name} is done!")
            offices = listing.find_all(class_='module-pd-office-item')
            office_names = []
            office_addresses = []
            for office in offices:
                try:
                    office_names.append(office.find(class_='office-detail').text.replace('\n', ''))
                except:
                    office_names.append('None')
                try:
                    office_addresses.append(office.find(class_='map')['href'].split('=')[1])
                except:
                    office_addresses.append('None')
            new_dict = {
                'Link': link,
                'Name': name,
                'Specialty': specialty,
                'Phone': phone,
                'Offices': office_names,
                'Addresses': office_addresses
            }
            DICT_LIST.append(new_dict)
        #print(f'Page {num} is done!')
        return DICT_LIST


def save_file_to_s3(bucket, file_name, data):
  s3 = boto3.resource('s3')
  obj = s3.Object(bucket, file_name)
  obj.put(Body=json.dumps(data))
'''
def scrape(event, context):
  data = deal_scrape()
  file_name = f"deals-{data['date']}"
  save_file_to_s3('ebay_daily_deals', file_name, data)
'''
def lambda_handler(event, context):
    data = scrape()
    save_file_to_s3(bucket, file_name, data)
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    # try:
    #     ip = requests.get("http://checkip.amazonaws.com/")
    # except requests.RequestException as e:
    #     # Send some context about this error to Lambda Logs
    #     print(e)

    #     raise e

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "scrape successfull",
            # "location": ip.text.replace("\n", "")
        }),
    }
