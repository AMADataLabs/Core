'''Scrapes Becker Review and sends email'''
import os
from datetime import date
import pandas as pd
import settings
from scrape import get_soup, extract_data
from auto_email import send_email

def get_email_parameters(file_1, file_2, today):
    '''Get parameters'''
    full = ['Lauren.McConnell@ama-assn.org']
    just_me = ['victoria.grose@ama-assn.org', 'Sandeep.Dhamale@ama-assn.org']
    subject = f'Hospital COVID-19 Furloughs for {today}'
    body = '''
Hi,

This is an automated email from DataLabs. Please find all new content in attachments.

Note: The scraping activity happens every morning at 9:00 am. If you would like the results at another time or would like to stop this service, kindly reply to this email.

Thank you!
DataLabs
'''
    attachments = [file_1, file_2]
    auto_send = True
    return full, just_me, subject, body, attachments, auto_send

def get_delta(yesterday, today):
    '''Find change since last email'''
    intersect = list(pd.merge(yesterday, today, on=list(yesterday.columns))['Location'])
    delta = today[today.Location.isin(intersect) == False]
    return delta

def get_yesterday(path):
    '''Return newest dataframe from folder'''
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files if 'Hospital_Furloughs' in basename]
    yesterday_file = max(paths, key=os.path.getctime)
    yesterday = pd.read_excel(yesterday_file)
    return yesterday

def main():
    '''MAIN'''
    today = str(date.today())
    url = os.environ.get('URL')
    out_dir = os.environ.get('OUT_DIRECTORY')
    furlough_file = f'{out_dir}Hospital_Furloughs_{today}.xlsx'
    furlough_delta_file = f'{out_dir}Hospital_Furlough_Delta_{today}.xlsx'

    print('Accessing site...')
    soup = get_soup(url)
    print('Extracting data...')
    data = extract_data(soup)
    print('Saving ')
    furloughs = pd.DataFrame(data)
    print('Getting delta...')
    yesterday_furloughs = get_yesterday(out_dir)
    furlough_delta = get_delta(yesterday_furloughs, furloughs)
    print('Saving ')
    furlough_delta.to_excel(furlough_delta_file, index=False)
    furloughs.to_excel(furlough_file, index=False)
    print('Emailing results...')
    full, just_me, subject, body, attachments, auto_send = get_email_parameters(
        furlough_file, furlough_delta_file, today)
    send_email(full, just_me, subject, body, attachments, auto_send)


if __name__ == "__main__":
    main()
