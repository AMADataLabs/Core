import json
import logging
import os
from json import JSONEncoder

import boto3
import pymysql
import requests
import suds_requests
from suds.client import Client
from suds.wsse import *

port = 3306
logger = logging.getLogger()
logger.setLevel(logging.INFO)
ssm = boto3.client('ssm', region_name=os.environ['AWS_REGION'])
tam_id = ''
user_name = ''
user_email = ''
ama_user_name = ''
fname = ''
lname = ''


class UserObjectDictionary:
    pass


class ObjectEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


def addsecurityheader(client, username, password):
    security = Security()
    userNameToken = UsernameToken(username, password)
    timeStampToken = Timestamp(validity=600)
    security.tokens.append(userNameToken)
    security.tokens.append(timeStampToken)
    client.set_options(wsse=security)


def check_if_email_exists(user_email, conn):
    user_status_query = 'Select User.user_name, User.tam_id, User.is_active from User where User.email = %s'
    try:
        cur = conn.cursor()
        cur.execute(user_status_query, user_email)
        records = cur.fetchall()
    except Exception as ex:
        logger.error("ERROR: Could not get User using email id" + str(ex))
    finally:
        cur.close()
    if len(records) > 0:
        row = records[0]
        return {
            'row_count': 1,
            'user_name': row[0],
            'tam_id': row[1],
            'is_active': row[2]
        }
    else:
        return {
            'row_count': 0,
            'user_name': '',
            'tam_id': '',
            'is_active': ''
        }


def add_user_to_dev_portal(userName, env):
    url = ssm.get_parameter(Name='/mfoneview/' + env + '/usradmin/service-url', WithDecryption=True)['Parameter'][
        'Value']
    username = ssm.get_parameter(Name='/mfoneview/' + env + '/usradmin/user-name', WithDecryption=True)['Parameter'][
        'Value']
    password = os.environ.get("DATABASE_PASSWORD")
    session = requests.session()
    session.auth = (username, password)
    client = Client(url, faults=False, cachingpolicy=1, location=url,
                    transport=suds_requests.RequestsTransport(session))
    addsecurityheader(client, username, password)
    default_roles = ["Internal/everyone", "Internal/subscriber"]
    claims = []
    return_code, message = client.service.addUser(userName, "abcd123", default_roles, claims, '', False)
    if return_code != 200:
        logger.error("ERROR: Unexpected error: Could not add user - " + userName + str(message))
    return return_code


def update_user_tam_id(conn):
    update_query = """UPDATE User set fname = %s, lname = %s, user_name = %s, tam_id = %s, is_active = %s 
        where User.email = %s'"""
    try:
        cur = conn.cursor()
        cur.execute(update_query, (fname, lname, ama_user_name, tam_id, '1', user_email))
        row_count = cur.rowcount
        conn.commit()
    except Exception as ex:
        logger.error("ERROR: Could not update the user record")
        logger.error(ex)
    finally:
        cur.close()
    if row_count < 0:
        logger.error("ERROR: Could not update the user record")
        return {
            'statusCode': 500,
            'body': 'There was an issue while updating the user'
        }
    else:
        return {
            'statusCode': 200,
            'body': 'new'
        }


def update_user_details(event, conn):
    row_count: int = -1
    update_query = 'UPDATE User set fname = %s, lname = %s, user_name = %s, email = %s where User.tam_id = %s'
    try:
        cur = conn.cursor()
        cur.execute(update_query, (fname, lname, ama_user_name, user_email, tam_id))
        row_count = cur.rowcount
        conn.commit()
    except Exception as ex:
        logger.error("ERROR: Could not update the user record" + str(ex))
    finally:
        cur.close()
    if row_count < 0:
        logger.error("ERROR: Could not update the user record")
        return {
            'statusCode': 500,
            'body': 'Could not update the user record'
        }
    else:
        return {
            'statusCode': 200,
            'body': 'existing'
        }


def get_org_id(conn):
    domain_name = user_email[user_email.rindex("@") + 1:]
    logger.info('Domain name is ' + domain_name)
    get_org_id_query = """SELECT Organization.id FROM Organization, Domains, 
    Organization_Domains where Organization.id = Organization_Domains.organization_id and 
    Domains.id = Organization_Domains.domain_id and 
    INSTR(UPPER(Domains.domain_name), UPPER(\'""" + domain_name + "\'))"
    records = 0
    row_count = 0
    try:
        cur = conn.cursor()
        cur.execute(get_org_id_query)
        records = cur.fetchall()
    except Exception as ex:
        logger.error("ERROR: Could not get the Org Id" + str(ex))
    finally:
        cur.close()
    if len(records) > 0:
        row = records[0]
        return row[0]
    else:
        return 3 # default org id is 3, i.e AMA Association.


def get_profile_id(conn, org_id):
    profile_id = None
    get_profile_query = """
                        SELECT Groups.id from Groups where Groups.organization_id = %s AND Groups.default = %s
                        """
    try:
        cur = conn.cursor()
        cur.execute(get_profile_query, (str(org_id), '1'))
        row_count = cur.rowcount
        if row_count == 0:
            raise Exception("ERROR: Could not get the default profile for org " + str(org_id))
        else:
            records = cur.fetchone()
            profile_id = records[0]
    except Exception as ex:
        logger.error("ERROR: Could not get the default profile for org " + str(org_id))
        logger.info(ex)
    finally:
        cur.close()
    return profile_id


def get_department_id(conn, org_id):
    department_id = None
    get_default_department_id_query = """ SELECT Departments.id FROM Departments WHERE Departments.organization_id = %s 
                                            AND Departments.default = %s    
                                        """
    get_department_id_query = """ SELECT Departments.id FROM Departments WHERE Departments.organization_id = %s """
    try:
        cur = conn.cursor()
        cur.execute(get_default_department_id_query, (str(org_id), '1'))
        row_count = cur.rowcount
        if row_count == 0:
            cur.execute(get_department_id_query, str(org_id))
            records = cur.fetchone()
        else:
            records = cur.fetchone()
        if len(records) > 0:
            department_id = records[0]
        else:
            raise Exception("ERROR: Could not get the default department for org " + str(org_id))
    except Exception as ex:
        logger.error("ERROR: Could not get the default department for org " + str(org_id))
        logger.info(ex)
    finally:
        cur.close()
    return department_id


def add_user_details(conn):
    insert_query = """INSERT INTO User (fname, lname, mname, email, org_id, tam_id, user_name, is_admin, 
    department_id, is_active) values (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    assign_profile_query = """
                            INSERT INTO User_Group_Assignment (user_id, group_id) values (%s,%s)
                            """
    row_count = 0
    org_id = get_org_id(conn)
    logger.info('org id is' + str(org_id))
    department_id = get_department_id(conn, org_id)
    if not department_id:
        raise Exception("ERROR: Unable to get default department")
    else:
        logger.info('default department id is' + str(department_id))
    profile_id = get_profile_id(conn, org_id)
    if not profile_id:
        raise Exception("ERROR: Unable to get default profile")
    else:
        logger.info('default profile id is' + str(profile_id))
    try:
        cur = conn.cursor()
        cur.execute(insert_query,
                    (fname, lname, '', user_email, str(org_id), tam_id, ama_user_name, '0', str(department_id), '1'))
        user_id = cur.lastrowid
        cur.execute(assign_profile_query, (user_id, profile_id))
        row_count = cur.rowcount
        conn.commit()
    except Exception as ex:
        logger.error("ERROR: Could not Insert the user record")
        logger.info(ex)
    finally:
        cur.close()
    if row_count > 0:
        return {
            'statusCode': 200,
            'body': 'new'
        }
    else:
        return {
            'statusCode': 500,
            'body': 'Could not register new user'
        }


def lambda_handler(event, context):
    global tam_id
    tam_id = event['tamId']
    global user_name
    user_name = event['amaName']
    global ama_user_name
    ama_user_name = event['userName']
    arn = context.invoked_function_arn
    global lname
    lname = user_name[user_name.rindex(" ") + 1:]
    global fname
    fname = user_name[0:user_name.rindex(" ")]
    lastIndex = arn.rindex(':') + 1
    global user_email
    user_email = event['email']
    run_environment = arn[lastIndex:]
    db_host = os.environ.get("DATABASE_HOST")
    user_id = os.environ.get("DATABASE_USERNAME")
    password = os.environ.get("DATABASE_PASSWORD")
    dbname = os.environ.get("DATABASE_NAME")
    select_query = 'SELECT User.is_active from User where User.tam_id = %s'
    records: list = []

    try:
        conn = pymysql.connect(db_host, user=user_id,
                               passwd=password, db=dbname, connect_timeout=50)
        cur = conn.cursor()
        cur.execute(select_query, (tam_id))
        records = cur.fetchall()
        if len(records) > 0:
            row = records[0]
            if row[0] == 1:  # is_active = true
                return json.loads(json.dumps(update_user_details(event, conn), cls=ObjectEncoder))
            else:  # is_active = false
                return {
                    'statusCode': 200,
                    'body': 'inactive'
                }
        else:
            user_status = check_if_email_exists(user_email, conn)
            if user_status['row_count'] > 0:
                return json.loads(json.dumps(update_user_tam_id(conn), cls=ObjectEncoder))
            else:
                return json.loads(json.dumps(add_user_details(conn), cls=ObjectEncoder))
    except Exception as ex:
        logger.error("ERROR: Unexpected error: Could not validate User")
        logger.error(ex)
    finally:
        conn.close()
