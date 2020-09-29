import win32com.client as win32
import errno
import os
from datetime import datetime, date
import settings 

def get_parameters():
    '''Get email parameters'''
    today = str(date.today())
    out = os.environ.get('OUT_DIR')
    out_directory = f'{out}{today}'
    file1 = f'{out_directory}/Other_Physicians_Unprocessed_{today}.xlsx'
    file2 = f'{out_directory}/Memorium_USA_Physicians_Unprocessed_{today}.xlsx'
    full = ['Chris.Mathews@ama-assn.org', 'Clint.Sheffer@ama-assn.org', 'sandeep.dhamale@ama-assn.org']
    meonly = ['victoria.grose@ama-assn.org']
    subject = f'COVID-19 Mortality Data –  {today}'
    body = '''Hi,

    This is an automated email from DataLabs. Please find all new content in attachments.
    
    
    NOTE: The scraping activity happens every morning at 8:55 am and the results are emailed at 9:00 am. 
    If you would like the results at another time or would like to stop this service, kindly reply to this email.
    
    Thank you!
    DataLabs
    '''
    attachments = [file1, file2]
    return (full, meonly, subject, body, attachments)

def send_email(auto_send=True):
    '''Send le email'''
    outlook = win32.Dispatch('outlook.application')
    recipients, cc, subject, body, attachments = get_parameters()
    if len(recipients) == 0 or len(subject) == 0 or len(body) == 0:
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
