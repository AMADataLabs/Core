import json
import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from json import JSONEncoder

import boto3
import pymysql

# set port to 3306
port = 3306
logger = logging.getLogger()
logger.setLevel(logging.INFO)
ssm = boto3.client('ssm', region_name=os.environ['AWS_REGION'])


class usersList_Dict:
    pass


class ObjectEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


def get_department_admin(conn, department_id):
    data_records = []
    select_query = """
                    SELECT
                    a.email, b.email
                FROM
                    User a,
                    Departments,
                    User b
                WHERE
                    Departments.id = %s and
                    Departments.primary_admin = a.id and
                    Departments.backup_admin = b.id
    """
    try:
        cur = conn.cursor()
        cur.execute(select_query, department_id)
        data_records = cur.fetchall()
        conn.commit()
    except Exception as ex:
        logger.error("ERROR: Could not get primary and backup admin details")
    finally:
        cur.close()
    return data_records[0]


def get_user_name(conn, user_id):
    user_full_name = ''
    select_query = """SELECT fname, lname FROM User WHERE User.id = %s"""
    try:
        cur = conn.cursor()
        cur.execute(select_query, user_id)
        data_records = cur.fetchall()
        conn.commit()
    except Exception as ex:
        logger.error("ERROR: Could not get user name")
    finally:
        cur.close()
    if len(data_records) > 0:
        user_full_name = data_records[0][0] + ' ' + data_records[0][1]
    return user_full_name


def send_email_with_smtp(run_environment, user_full_name, department_name, admins, description):
    from_email = \
        ssm.get_parameter(Name='/mfoneview/' + run_environment + '/usrmgmt/fromEmail', WithDecryption=True)[
            'Parameter']['Value']
    from_email_password = \
        ssm.get_parameter(Name='/mfoneview/' + run_environment + '/usrmgmt/smtpPassword', WithDecryption=True)[
            'Parameter']['Value']
    smtpURL = \
        ssm.get_parameter(Name='/mfoneview/' + run_environment + '/usrmgmt/smtpURL', WithDecryption=True)['Parameter'][
    'Value']
    message_subject = "Welcome to the Data Labs Masterfile One View"
    email_body = None
    email_body_header = ' '
    email_body_header = email_body_header + '<html><head></head><body>'
    email_body_header = email_body_header + '<style type="text/css"></style>'
    email_body_header = email_body_header + '<br><p>Dear Admin,<br>'
    email_body_content = ' '
    email_body_content = email_body_content + '<p>User '
    email_body_content = email_body_content + user_full_name
    email_body_content = email_body_content + ' has requested access to department '
    email_body_content = email_body_content + department_name
    email_body_content = email_body_content + '  as follows</p>'

    email_body_content = email_body_content + '<p>'
    email_body_content = email_body_content + description
    email_body_content = email_body_content + '</p>'

    email_body_footer = ' '
    email_body_footer = email_body_footer + '<br>Regards'
    email_body_footer = email_body_footer + '<br>Developer Portal Support<br>'
    email_body_footer = email_body_footer + '<br>AMA Health Solutions Group<br>'
    email_body_footer = email_body_footer + '<br>platform@ama-assn.org<br>'
    email_body = str(email_body_header) + str(email_body_content) + str(email_body_footer)

    for email_id in admins:
        message = MIMEMultipart('alternative')
    message['From'] = from_email
    message['To'] = email_id
    message['Subject'] = message_subject
    body = email_body
    message.attach(MIMEText(body, 'html'))
    try:
        smtp_object = smtplib.SMTP(smtpURL)
        smtp_object.starttls()
        smtp_object.login(from_email, from_email_password)
        smtp_object.sendmail(from_email, email_id, message.as_string())
    except smtplib.SMTPException as e:
        logger.error(str(e))
        return 500
    return 200


def get_department_name(conn, department_id):
    department_name = ''
    select_department_query = 'Select name from Departments where id = %s'
    try:
        cur = conn.cursor()
        cur.execute(select_department_query, (str(department_id)))
        records = cur.fetchall()
        row_count = cur.rowcount
        if row_count > 0:
            department_name = records[0][0]
    except Exception as ex:
        logger.error("ERROR: Could not Insert the user record")
        logger.error(str(ex))
    finally:
        cur.close()

    return department_name


def lambda_handler(event, context):
    success = True
    arn = context.invoked_function_arn
    lastIndex = arn.rindex(':') + 1
    runEnvironment = arn[lastIndex:]
    user_id = os.environ.get("DATABASE_USERNAME")
    user_name = event["username"]
    organization_id = event["orgId"]
    department_id = event["departmentId"]
    description = event["description"]
    db_host = os.environ.get("DATABASE_HOST")
    user_id = os.environ.get("DATABASE_USERNAME")
    password = os.environ.get("DATABASE_PASSWORD")
    dbname = os.environ.get("DATABASE_NAME")
    try:
        conn = pymysql.connect(host=db_host, user=db_user_id,
                               passwd=password, db=dbname, connect_timeout=50)
        admins = []
        admins = get_department_admin(conn, department_id)
        department_name = ''
        department_name = get_department_name(conn, department_id)
        user_full_name = ''
        user_full_name = get_user_name(conn, user_id)
        if len(user_full_name) > 0:
            rc = send_email_with_smtp(runEnvironment, user_full_name, department_name, admins, description)
            if rc != 200:
                success = False
                raise Exception("Error: There was an error sending an email to Department admin")
        else:
            raise Exception("Error: There was an error retrieving User name")
            success = False
    except Exception as ex:
        logger.error("ERROR: Unexpected error: Could not process user request")
        logger.error(ex)
        success = False
    finally:
        conn.close()

    return_obj = usersList_Dict()
    if success:
        return_obj.returnCode = 200
    else:
        return_obj.returnCode = 500
        return_obj.errMessage = 'Unable to process request at this time'

    return json.loads(json.dumps(return_obj, cls=ObjectEncoder))
