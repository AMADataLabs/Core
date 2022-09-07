import win32com.client as win32
import errno
import os
from datetime import date
import pandas as pd
# from   dataclasses import dataclass
# from   datetime import datetime
# from   io import BytesIO
# import pickle

# from datalabs.etl.load import LoaderTask
# from datalabs.messaging.email_message import Attachment, send_email
# from datalabs.parameter import add_schema

def get_parameters():
    '''Get email parameters'''
    today = str(date.today())
    test = 'C:/Users/vigrose/Data/License/NC_License_Status_2022-06-14.csv'
    # full = ['chris.mathews@ama-assn.org']
    full = ['victoria.grose@ama-assn.org']
    meonly = ['victoria.grose@ama-assn.org']
    subject = f'Email Test –  {today}'
    body = f'''Hi,

    This is an automated email from DataLabs. Please find all new content in attachments. 

    All files contain only records that have been modified since the previous scrape.

    Thanks,

    Victoria
    '''
    attachments = [test]
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