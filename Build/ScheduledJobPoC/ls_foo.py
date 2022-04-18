import pysftp

cnopts = pysftp.CnOpts()
cnopts.hostkeys = None

with pysftp.Connection('eft.ama-assn.org', username=os.environ['SFTP_USERNAME'], password=os.environ['SFTP_USERNAME'], cnopts=cnopts) as sftp:
    with sftp.cd('Data Analytics/Peter'):
        for attr in sftp.listdir_attr():
            print(attr.filename, attr)
