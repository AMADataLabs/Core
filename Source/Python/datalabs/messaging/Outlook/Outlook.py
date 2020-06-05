import os
import errno
import win32com.client as win32


outlook = win32.Dispatch('outlook.application')


def add_attachments(msg, attachments):
    for attachment in attachments:
        if os.path.exists(attachment):
            msg.Attachments.Add(attachment)
        else:
            msg.Delete()
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), attachment)


def set_msg_sender(msg, account_name):
    for acc in outlook.Session.Accounts:
        if acc.SmtpAddress.lower() == account_name.lower():
            msg._oleobj_.Invoke(*(64209, 0, 8, 0, acc))  # msg.SendUsingAccount = acc_to_use
            return
    raise ValueError(f'Account {account_name} not found in active Outlook accounts.\n'
                     f'Try checking your settings in Outlook to add the account.')


"""
Sends an email.
Requirements
   outlook: win32com.client.Dispatch('outlook.application')
   Outlook must be running on the system running this code.
   The following parameters MUST be defined:
      * to
      * subject
Notes
   - There is no check on the validity of email addresses in to and cc
   - Method will fail if attachments are specified but not found.
Parameters
   to:            email address (string) or list of email addresses (strings)
   cc:            email address (string) or list of email addresses (strings)
   subject:       email message subject (string)
   body:          email message body text (string)
   attachments:   absolute path (string) or list of absolute paths (strings) to desired email attachments.
     Ex: ['C:\\Documents\\file_A.csv', 'C:\\Documents\\file_B.csv']
   auto_send:     whether or not the method sends the email (if not, message will display in Outlook)
"""


def send_email(to, subject, cc=None, body='', attachments=None, from_account=None, auto_send=True):

    msg = outlook.CreateItem(0)

    if isinstance(to, str):
        to = [to]
    assert isinstance(to, list)
    msg.To = '; '.join(to)

    if cc is not None:
        if isinstance(cc, str):
            cc = [to]
        assert isinstance(cc, list)
        msg.Cc = '; '.join(cc)

    msg.Subject = subject

    if body is not None:
        msg.Body = body

    # Find Account object by name
    if from_account is not None:
        set_msg_sender(msg, from_account)

    if attachments is not None:
        if isinstance(attachments, str):
            attachments = [attachments]
        add_attachments(msg, attachments)

    # If you don't want to automatically send the email from this script,
    # you can opt to display the email in Outlook on the desktop for
    # you to review and hit 'Send' manually as you would with a normal email.
    if auto_send:
        msg.Send()
    else:
        msg.Display(True)

