import pandas as pd
import requests
import xmltodict
import json
import matplotlib.pyplot as plt
from fuzzywuzzy import fuzz
from dataclasses import dataclass, asdict

@dataclass
class NumberSearch:
    number: int = ''
    version: str = '2.1'
    enumeration_type: any = 'NPI-1'

def get_results(search):
    url = 'https://npiregistry.cms.hhs.gov/api/?version=2.1'
    parameters = asdict(search)
    response =  requests.get(url, params=parameters)
    try:
        results = response.json()
    except:
        results = False
    return results
    
def get_npi_info(results):
    new_dict_list =[]
    try:
        result = results['results'][0]
        npi = result['number']
        for address in result['addresses']:
            zipcode = address['postal_code']
            state = address['state']
            new_dict = {
                'NPI': npi,
                'STATE': state,
                'ZIP': zipcode
            }
            new_dict_list.append(new_dict)
    except:
        new_dict_list = False
    return new_dict_list