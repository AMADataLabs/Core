from io import BytesIO
from datalabs.messaging.email_message import send_email, Attachment


a = Attachment(file_path='dog.jpg')
with open('test_attachment.txt', 'rb') as f:
    a2 = Attachment(name='test_att.txt', data=BytesIO(f.read()))

send_email(to='garrett.lappe@ama-assn.org', from_account='garrett.lappe@ama-assn.org', subject='test',
           attachments=[a, a2])
