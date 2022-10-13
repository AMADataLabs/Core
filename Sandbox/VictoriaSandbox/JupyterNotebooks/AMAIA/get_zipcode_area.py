#Import dependencies:
from bs4 import BeautifulSoup
import requests

#Make sure zipcode is 5 digits
def clean_zipcode(zipcode):
    zipcode=str(zipcode)
    zipcode = zipcode.replace(".0","")
    if len(zipcode)==3:
        zipcode = "00"+zipcode
    if len(zipcode)==4: 
        zipcode = "0"+zipcode
    else:
        zipcode = zipcode[0:5]
    return(zipcode)

#Get land area for single zipcode
def get_zipcode_land_area(zipcode):
    zipcode = clean_zipcode(zipcode)
    url = f'https://www.zip-codes.com/zip-code/{zipcode}/zip-code-{zipcode}.asp'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    rows = soup.find_all('tr')
    for row in rows:
        if row.find('td').text =='Land Area:':
            land_area = row.find(class_ = 'info').text
            break
    return(land_area)