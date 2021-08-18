import json
import logging
import os
import sys
from json import JSONEncoder
import boto3
import pymysql
from suds.wsse import *

port = 3306
logger = logging.getLogger()
logger.setLevel(logging.INFO)
ssm = boto3.client('ssm', region_name=os.environ['AWS_REGION'])


class ObjectEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


def addSecurityHeader(client, username, password):
    security = Security()
    userNameToken = UsernameToken(username, password)
    timeStampToken = Timestamp(validity=600)
    security.tokens.append(userNameToken)
    security.tokens.append(timeStampToken)
    client.set_options(wsse=security)


def lambda_handler(event, context):
    arn = context.invoked_function_arn
    lastIndex = arn.rindex(':') + 1
    runEnvironment = arn[lastIndex:]
    # runEnvironment = 'test'
    last_updated_by = event['updatedBy']
    tamId = event['tamId']
    firstName = event['firstName']
    middleName = ''
    lastName = event['lastName']
    addr1 = event['addr1']
    addr2 = event['addr2']
    addr3 = event['addr3']
    city = event['city']
    state = event['state']
    zip = event['zip']
    phone = event['phone']

    db_host = os.environ.get("DATABASE_HOST")
    user_id = os.environ.get("DATABASE_USERNAME")
    ssm.get_parameter(Name='/mfoneview/' + runEnvironment + '/usrmgmt/user-name', WithDecryption=True)['Parameter'][
        'Value']
    password = os.environ.get("DATABASE_PASSWORD")
    ssm.get_parameter(Name='/mfoneview/' + runEnvironment + '/usrmgmt/password', WithDecryption=True)['Parameter']['Value']
    dbname = os.environ.get("DATABASE_NAME")
    try:
        conn = pymysql.connect(host=db_host, user=user_id,
                               passwd=password, db=dbname, connect_timeout=50)
    except:
        logger.error("ERROR: Unexpected error: Could not connect to MySql instance.")
        sys.exit()
    row_count = 0
    try:
        cur = conn.cursor()
        query = 'UPDATE User set fname = %s, mname = %s, lname = %s, addr1 = %s, addr2 = %s, addr3 = %s, city = %s, state = %s, zip = %s, phone = %s, last_updated_by = %s where User.tam_id = %s'
        cur.execute(query, (
        firstName, middleName, lastName, addr1, addr2, addr3, city, state, zip, phone, str(last_updated_by), tamId))
        row_count = cur.rowcount
        conn.commit()
    except Exception as ex:
        logger.error("ERROR: Could not update the table")
        print(ex)
    finally:
        cur.close()
        conn.close()
    if (row_count < 0):
        return {
            'statusCode': 500,
            'body': json.dumps("Error: Something went wrong while updating the User ")
        }
    else:
        return {
            'statusCode': 200,
            'body': json.dumps("User details updated Successfully")
        }
