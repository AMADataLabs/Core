'''
Sends an email.
Requirements
   outlook: win32com.client.Dispatch('outlook.application')
   The following parameters MUST be defined:
      * recipients
      * subject
      * body
Warning
   There is no check on the validity of email addresses.
   Email address data in recipients and cc must be verified by caller.
   Method will fail if attachments are specified but not found.
Parameters
   recipients:    list of email addresses (strings)
   cc:            list of email addresses (strings)
   subject:       email message subject (string)
   body:          email message body text (string)
   attachments:   list of paths to desired email attachments.
     Ex: ['C:\\Documents\\file_A.csv', 'C:\\Documents\\file_B.csv']
   auto_send:     whether or not the method sends the email
   (if not, message will display in Outlook)
'''

import errno
import os
import win32com.client as win32

OUTLOOK = win32.Dispatch('outlook.application')

def send_email(recipients, cc, subject, body, attachments, auto_send):
    '''Sends email'''
    if len(recipients) == 0 or len(subject) == 0 or len(body) == 0:
        raise ValueError('recipients, subject, and body must be defined.')
    msg = OUTLOOK.CreateItem(0)
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
