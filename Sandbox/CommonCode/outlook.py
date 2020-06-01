import os
import errno
import win32com.client as win32


outlook = win32.Dispatch('outlook.application')


# Helper for parsing arguments for to and cc parameters. The idea is to process both strings and lists of strings.
def parse_email_addresses(param):

    if isinstance(param, str):
        return param
    elif isinstance(param, list):
        return '; '.join(param)
    else:
        raise ValueError(f'Argument {param} not parsed properly. Please pass string or list of strings.')


# Sends an email.
# Requirements
#    outlook: win32com.client.Dispatch('outlook.application')
#    Outlook must be running on the system running this code.
#    The following parameters MUST be defined:
#       * to
#       * subject
# Notes
#    - There is no check on the validity of email addresses in to and cc
#    - Method will fail if attachments are specified but not found.
# Parameters
#    to:            email address (string) or list of email addresses (strings)
#    cc:            email address (string) or list of email addresses (strings)
#    subject:       email message subject (string)
#    body:          email message body text (string)
#    attachments:   absolute path (string) or list of absolute paths (strings) to desired email attachments.
#      Ex: ['C:\\Documents\\file_A.csv', 'C:\\Documents\\file_B.csv']
#    auto_send:     whether or not the method sends the email (if not, message will display in Outlook)
def send_email(to, subject, cc=None, body='', attachments=None, from_account=None, auto_send=True):

    msg = outlook.CreateItem(0)

    msg.To = parse_email_addresses(to)

    if cc is not None:
        msg.Cc = parse_email_addresses(cc)

    msg.Subject = subject

    if body is not None:
        msg.Body = body

    # Find Account object by name
    if from_account is not None:
        acc_to_use = None
        for acc in outlook.Session.Accounts:
            if acc.SmtpAddress.lower() == from_account.lower():
                acc_to_use = acc

        if acc_to_use is None:
            raise ValueError(f'Account {from_account} not found in active Outlook accounts.\n'
                             f'Try checking your settings in Outlook to add the account.')
        msg._oleobj_.Invoke(*(64209, 0, 8, 0, acc_to_use))  # msg.SendUsingAccount = acc_to_use)

    # Attachments
    if attachments is not None:
        if isinstance(attachments, str):
            attachments = [attachments]  # if a single path is given, make it a list of size 1 for this upcoming loop.
        for attachment in attachments:
            if os.path.exists(attachment):
                msg.Attachments.Add(attachment)
            else:
                msg.Delete()
                raise FileNotFoundError(
                    errno.ENOENT, os.strerror(errno.ENOENT), attachment)

    # If you don't want to automatically send the email from this script,
    # you can opt to display the email in Outlook on the desktop for
    # you to review and hit 'Send' manually as you would with a normal email.
    if auto_send:
        msg.Send()
    else:
        msg.Display(True)
