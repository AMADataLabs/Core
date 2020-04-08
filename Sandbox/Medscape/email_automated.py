import win32com.client as win32
import errno
import os
from datetime import datetime, date

outlook = win32.Dispatch('outlook.application')
# TODAY = str(datetime.now()).split('.')[0].replace(' ', '_').replace(':', '')
TODAY = str(date.today())

# Sends an email.
# Requirements
#    outlook: win32com.client.Dispatch('outlook.application')
#    The following parameters MUST be defined:
#       * recipients
#       * subject
#       * body
# Warning
#    There is no check on the validity of email addresses.
#    Email address data in recipients and cc must be verified by caller.
#    Method will fail if attachments are specified but not found.
# Parameters
#    recipients:    list of email addresses (strings)
#    cc:            list of email addresses (strings)
#    subject:       email message subject (string)
#    body:          email message body text (string)
#    attachments:   list of paths to desired email attachments.
#      Ex: ['C:\\Documents\\file_A.csv', 'C:\\Documents\\file_B.csv']
#    auto_send:     whether or not the method sends the email (if not, message will display in Outlook)

OUT_DIRECTORY = f'C:\\Users\\nkhatri\\OneDrive - American Medical Association\\Documents\\Task-Scheduled\\{str(date.today())}'
# C:\Users\nkhatri\OneDrive - American Medical Association\Documents\Task-Scheduled\2020-04-08
# OUT_DIRECTORY = f'C:/Users/nkhatri/OneDrive - American Medical Association/Documents/Task-Scheduled/{TODAY}'
file1 = f'{OUT_DIRECTORY}\\Memorium_{TODAY}.csv'
file2 = f'{OUT_DIRECTORY}\\Memorium_USA_{TODAY}.csv'
file3 = f'{OUT_DIRECTORY}\\Memorium_USA_Physicians_{TODAY}.csv'
file4 = f'{OUT_DIRECTORY}\\Memorium_USA_ME_{TODAY}.csv'
file5 = f'{OUT_DIRECTORY}\\AGE_{TODAY}.png'
file6 = f'{OUT_DIRECTORY}\\ROLE_{TODAY}.png'
file7 = f'{OUT_DIRECTORY}\\STATE_{TODAY}.png'
file8 = f'{OUT_DIRECTORY}\\USA_Stats_{TODAY}.xlsx'
#'Chris.Mathews@ama-assn.org', 'Clint.Sheffer@ama-assn.org', 'Nicole.Neal@ama-assn.org','Tammy.Weaver@ama-assn.org', 'Derek.Smart@ama-assn.org', 'victoria.grose@ama-assn.org','sandeep.dhamale@ama-assn.org'

def send_email(recipients=['nikhil.khatri@ama-assn.org' ], cc=['nikhil.khatri@ama-assn.org'],
               subject='COVID-19 Mortality Data – Medscape for”' + ' ' + TODAY,
               body='Hi,\nThis is an automated email from DataLabs. Please find all new content in attachments.\n \nNOTE: The scraping activity happens every morning at 8:55 am and the results are emailed at 9:00 am. If you would like the results at another time or would like to stop this service, kindly reply to this email.\n\nThank you!\nDataLabs',
               attachments=[file1, file2, file3, file4, file5, file6, file7, file8], auto_send=True):
    if len(recipients) == 0 or len(subject) == 0 or len(body) == 0:
        raise ValueError('recipients, subject, and body must be defined.')

    msg = outlook.CreateItem(0)

    to = '; '.join(recipients)
    msg.To = to

    cc = '; '.join(cc)
    msg.Cc = cc

    msg.Subject = subject

    msg.Body = body

    # Attachments
    for a in attachments:
        if os.path.exists(a):
            msg.Attachments.Add(a)
        else:
            msg.Delete()
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), a)

    # If you don't want to automatically send the email from this script,
    # you can opt to display the email in Outlook on the desktop for
    # you to review and hit 'Send' manually as you would with a normal email.
    if auto_send:
        msg.Send()
    else:
        msg.Display(True)


send_email()