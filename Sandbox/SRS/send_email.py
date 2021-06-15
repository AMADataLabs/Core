import win32com.client as win32
import errno
import os
from datetime import date
import pandas as pd
import settings 

def get_length(file_location):
    dataframe = pd.read_csv(file_location)
    return len(dataframe)


def get_parameters():
    '''Get email parameters'''
    today = str(date.today())
    out = os.environ.get('OUT_DIR')
    out_directory = f'{out}{today}'
    scraped_new = f'{out_directory}/SRS_Scrape_{today}.csv'
    matched = f'{out_directory}/SRS_Matched_{today}.csv'
    still_missing = f'{out_directory}/SRS_Missing_{today}.csv'
    stu_affil = f'{out_directory}/SRS_Student_Affiliates_{today}.csv'
    grad_year = f'{out_directory}/SRS_Graduation_Year_Discrepancy_{today}.csv'
    status_update = f'{out_directory}/SRS_Status_Discrepancy_{today}.csv'
    manual = f'{out_directory}/SRS_Manual_Updates_{today}.csv'
    auto = f'{out_directory}/SRS_Automatic_Updates_{today}.csv'
    new = f'{out_directory}/SRS_New_{today}.csv'
    unprocessed = f'{out_directory}/SRS_Unprocessed_{today}.csv'
    me_matched = matched[matched.me!='None']
    found_info = f'{out_directory}/SRS_AAMC_{today}.csv'
    found_students = get_length(found_info) - get_length(stu_affil)

    full = ['victoria.grose@ama-assn.org']
    meonly = ['victoria.grose@ama-assn.org']
    subject = f'Change of Status SRS Scrape –  {today}'
    body = f'''Hi,

    This is an automated email from DataLabs. Please find all new content in attachments.

    SRS_Matched includes all records that did not match back to an aamc_id but were matched back to our data on name, date of birth, etc. I included all of the matching fields and their ME number if it existed.
    SRS_Missing includes all records that did not match back on aamc_id or via the matching process.
    SRS_Graduation_Year_Discrepancy includes all record with graduation year discrepancies
    SRS_Status_Discrepancy includes all records with status differences.
    SRS_Student_Affiliates includes all records that matched on aamc_id but had a STU-AFFIL category code (these are excluded from all other files)

    SRS_Automatic_Updates includes records that would be theoretically automatically updated. We don’t have this process set up with IT at this time, so right now it’s for review only. 
    SRS_Manual_Updates includes records that require manual review
    SRS_New includes all new records (added or updated since the last scrape, in January). There is also a flag in every file attached indicating whether the record is new. In the future I would probably only send these records (the ones that are newer than the last scrape).


    {"{:,}".format(get_length(scraped_new))} student records in AAMC-SRS scrape
    {"{:,}".format(get_length(found_info))} ({round(get_length(found_info)/get_length(scraped_new)*100, 2)}%) records matched to AIMS on aamc_id
    {"{:,}".format(get_length(matched))} ({round(get_length(matched)/get_length(scraped_new)*100, 2)}%) records found via matching process 
    {"{:,}".format(len(me_matched))} ({round(len(me_matched)/get_length(scraped_new)*100, 2)}%) MEs appended via matching process
    {"{:,}".format(get_length(still_missing))} ({round(get_length(still_missing)/get_length(scraped_new)*100, 2)}%) scraped records missing from our database

    ----

    Of the records that matched on aamc_id
    {"{:,}".format(get_length(stu_affil))} ({round(get_length(stu_affil)/get_length(found_info)*100, 2)}%) records are student affiliates
    {"{:,}".format(found_students)} ({round(found_students)/get_length(found_info)*100, 2)}%) records are not student affiliates
        
    ----
    Of the records that are not student affiliates
    {"{:,}".format(get_length(grad_year))} ({round(get_length(grad_year)/get_length(found_students)*100, 2)}%) records have graduation year discrepancies
    {"{:,}".format(get_length(status_update))} ({round(get_length(status_update)/get_length(found_students)*100, 2)}%) records have status discrepancies, but correct graduation year

    ----

    {"{:,}".format(get_length(manual))} status discrepancies flagged for manual review
    {"{:,}".format(get_length(auto))} status discrepancies automatically processed
    {"{:,}".format(get_length(unprocessed))} status discrepancies not processed
    {"{:,}".format(get_length(new))} record updates since last scrape
    
    Thank you!
    DataLabs
    '''
    attachments = [scraped_new, matched, still_missing, grad_year, status_update, stu_affil, manual, auto]
    return (full, meonly, subject, body, attachments)

def send_email(auto_send=True):
    '''Send le email'''
    outlook = win32.Dispatch('outlook.application')
    recipients, cc, subject, body, attachments = get_parameters()
    if get_length(recipients) == 0 or get_length(subject) == 0 or get_length(body) == 0:
        raise ValueError('recipients, subject, and body must be defined.')
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