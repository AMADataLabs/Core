import os
import errno
import win32com.client as win32


class Outlook:

    def __init__(self):
        self.outlook = win32.Dispatch('outlook.application')

    def set_message_sender(self, message, account_name):
        account_found = False
        for acc in self.outlook.Session.Accounts:
            if acc.SmtpAddress.lower() == account_name.lower():
                # for information, see: https://stackoverflow.com/questions/52930447
                message._oleobj_.Invoke(*(64209, 0, 8, 0, acc))
                account_found = True
                break
        if not account_found:
            raise ValueError(f'Account {account_name} not found in active Outlook accounts.\n'
                             f'Try checking your settings in Outlook to add the account.')
        return


    def send_email(self, to, subject, cc=None, body='', attachments=None, from_account=None, auto_send=True):
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
        message = self.outlook.CreateItem(0)

        message.To = param_to_address_list(to)

        if cc is not None:
            message.Cc = param_to_address_list(cc)

        message.Subject = subject

        if body is not None:
            message.Body = body

        # Find Account object by name
        if from_account is not None:
            self.set_message_sender(message, from_account)

        if attachments is not None:
            if isinstance(attachments, str):
                attachments = [attachments]
            add_attachments(message, attachments)

        # If you don't want to automatically send the email from this script,
        # you can opt to display the email in Outlook on the desktop for
        # you to review and hit 'Send' manually as you would with a normal email.
        if auto_send:
            message.Send()
        else:
            message.Display(True)


def param_to_address_list(param):
    if param is not None:
        if not hasattr(param, '__iter__'):
            param = [param]
        param = '; '.join(param)
    return param


def add_attachments(message, attachments):
    for attachment in attachments:
        if os.path.exists(attachment):
            message.Attachments.Add(attachment)
        else:
            message.Delete()
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), attachment)
