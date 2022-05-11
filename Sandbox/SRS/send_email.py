import win32com.client as win32
import errno
import os
from datetime import date
import pandas as pd
import settings 
# from   dataclasses import dataclass
# from   datetime import datetime
# from   io import BytesIO
# import pickle

# from datalabs.etl.load import LoaderTask
# from datalabs.messaging.email_message import Attachment, send_email
# from datalabs.parameter import add_schema

def get_length_data(file_location):
    dataframe = pd.read_excel(file_location)
    return len(dataframe)

def get_parameters():
    '''Get email parameters'''
    today = str(date.today())
    out_directory = os.environ.get('OUT_DIR')
    scraped_new_all = f'{out_directory}/SRS_Scrape_{today}.xlsx'
    matched = f'{out_directory}/SRS_Matched_{today}.xlsx'
    still_missing = f'{out_directory}/SRS_Missing_{today}.xlsx'
    stu_affil = f'{out_directory}/SRS_Student_Affiliates_{today}.xlsx'
    grad_year = f'{out_directory}/SRS_Graduation_Year_Discrepancy_{today}.xlsx'
    status_update = f'{out_directory}/SRS_Status_Discrepancy_{today}.xlsx'
    manual = f'{out_directory}/SRS_Manual_Updates_{today}.xlsx'
    auto = f'{out_directory}/Automatic_Updates_{today}.xlsx'
    scraped_new = f'{out_directory}/SRS_Scraped_New_{today}.xlsx'
    unprocessed = f'{out_directory}/SRS_Unprocessed_{today}.xlsx'
    matched_ = pd.read_excel(matched)
    me_matched = matched_[matched_.me!='None']
    found_info = f'{out_directory}/SRS_AAMC_{today}.xlsx'
    found_students = get_length_data(found_info) - get_length_data(stu_affil)

    full = ['chris.mathews@ama-assn.org']
    # full = ['victoria.grose@ama-assn.org']
    meonly = ['victoria.grose@ama-assn.org']
    subject = f'Change of Status SRS Scrape –  {today}'
    body = f'''Hi,

    This is an automated email from DataLabs. Please find all new content in attachments. 

    All files contain only records that have been modified since the previous scrape.

    SRS_Scraped_New contains all records added or updated since the previous scrape.
    SRS_Matched includes all records that did not match back to an aamc_id but were matched back to our data on name, date of birth, etc. 
    SRS_Missing includes all records that did not match back on aamc_id or via the matching process. 
    SRS_Graduation_Year_Discrepancy includes all record with graduation year discrepancies 
    SRS_Status_Discrepancy includes all records with status differences. 
    SRS_Student_Affiliates includes all records that matched on aamc_id but had a STU-AFFIL category code (these are excluded from all other files)
    SRS_Automatic_Updates includes records that would be theoretically automatically updated. 
    SRS_Manual_Updates includes records that require manual review 

    {"{:,}".format(get_length_data(scraped_new_all))} student records in AAMC-SRS scrape
    {"{:,}".format(get_length_data(scraped_new))} record updates since last scrape
    {"{:,}".format(get_length_data(found_info))} ({round(get_length_data(found_info)/get_length_data(scraped_new)*100, 2)}%) records matched to AIMS on aamc_id
    {"{:,}".format(get_length_data(matched))} ({round(get_length_data(matched)/get_length_data(scraped_new)*100, 2)}%) records found via matching process 
    {"{:,}".format(len(me_matched))} ({round(len(me_matched)/get_length_data(scraped_new)*100, 2)}%) MEs appended via matching process
    {"{:,}".format(get_length_data(still_missing))} ({round(get_length_data(still_missing)/get_length_data(scraped_new)*100, 2)}%) scraped records missing from our database

    ----

    Of the records that matched on aamc_id
    {"{:,}".format(get_length_data(stu_affil))} ({round(get_length_data(stu_affil)/get_length_data(found_info)*100, 2)}%) records are student affiliates
    {"{:,}".format(found_students)} ({round((found_students)/get_length_data(found_info)*100, 2)}%) records are not student affiliates
        
    ----
    Of the records that are not student affiliates
    {"{:,}".format(get_length_data(grad_year))} ({round(get_length_data(grad_year)/found_students*100, 2)}%) records have graduation year discrepancies
    {"{:,}".format(get_length_data(status_update))} ({round(get_length_data(status_update)/found_students*100, 2)}%) records have status discrepancies, but correct graduation year

    ----

    {"{:,}".format(get_length_data(manual))} status discrepancies flagged for manual review
    {"{:,}".format(get_length_data(auto))} status discrepancies automatically processed
    {"{:,}".format(get_length_data(unprocessed))} status discrepancies not processed
    
        
    Thank you!
    DataLabs
    '''
    attachments = [scraped_new, matched, still_missing, grad_year, status_update, stu_affil, manual, auto]
    return (full, meonly, subject, body, attachments)

def send_email(auto_send=True):
    '''Send le email'''
    outlook = win32.Dispatch('outlook.application')
    recipients, cc, subject, body, attachments = get_parameters()
    # if get_length(recipients) == 0 or get_length(subject) == 0 or get_length(body) == 0:
    #     raise ValueError('recipients, subject, and body must be defined.')
    msg = outlook.CreateItem(0)
    to = '; '.join(recipients)
    msg.To = to
    cc = '; '.join(cc)
    msg.Cc = cc
    msg.Subject = subject
    msg.Body = body
    for a in attachments:
        if os.path.exists(a):
            msg.Attachments.Add(a)
        else:
            msg.Delete()
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), a)
    if auto_send:
        msg.Send()
    else:
        msg.Display(True)

if __name__ == "__main__":
    send_email()