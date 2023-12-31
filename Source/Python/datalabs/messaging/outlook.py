""" Class that sends email via Outlook on Windows machines. """
import os
import errno
import win32com.client as win32  # pylint: disable=import-error


class Outlook:
    def __init__(self):
        self.outlook = win32.Dispatch('outlook.application')

    #pylint: disable=invalid-name, too-many-arguments, too-many-statements
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

        # Find Account object by name
        if from_account is not None:
            self._set_message_sender(message, from_account)

        message.To = '; '.join(self._param_to_list(to))
        message.Cc = '; '.join(self._param_to_list(cc))

        message.Subject = subject

        # pylint: disable=pointless-statement
        message.GetInspector  # required for the next few lines inserting the body

        # Add body by inserting the text between the existing HTML body (which would contain any signatures)
        index = message.HTMLbody.find('>', message.HTMLbody.find('<body'))
        message.HTMLbody = message.HTMLbody[:index + 1] + body + message.HTMLbody[index + 1:]

        attachments = self._param_to_list(attachments)
        self._add_attachments(message, attachments)

        # If you don't want to automatically send the email from this script,
        # you can opt to display the email in Outlook on the desktop for
        # you to review and hit 'Send' manually as you would with a normal email.
        if auto_send:
            message.Send()
        else:
            message.Display(True)

    @classmethod
    def _param_to_list(cls, param):
        if param is None:
            param = []
        elif isinstance(param, str):
            param = [param]
        elif not hasattr(param, '__iter__'):
            raise TypeError(f"Parameter '{param}' is not a string or an iterable")
        return param

    def _set_message_sender(self, message, account_name):
        account_found = False
        for acc in self.outlook.Session.Accounts:
            if acc.SmtpAddress.lower() == account_name.lower():
                # for information, see: https://stackoverflow.com/questions/52930447
                message._oleobj_.Invoke(*(64209, 0, 8, 0, acc))  # pylint: disable=protected-access
                account_found = True
                break
        if not account_found:
            raise ValueError(f'Account {account_name} not found in active Outlook accounts.\n'
                             f'Try checking your settings in Outlook to add the account.')

    @classmethod
    def _add_attachments(cls, message, attachments):
        for attachment in attachments:
            if os.path.exists(attachment):
                message.Attachments.Add(attachment)
            else:
                message.Delete()
                raise FileNotFoundError(
                    errno.ENOENT, os.strerror(errno.ENOENT), attachment)
