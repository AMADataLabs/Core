import json
import logging
import os
from json import JSONEncoder

import boto3
import pymysql

port = 3306
logger = logging.getLogger()
logger.setLevel(logging.INFO)
ssm = boto3.client('ssm', region_name=os.environ['AWS_REGION'])


def lambda_handler(event, context):
    arn = context.invoked_function_arn
    last_index = arn.rindex(':') + 1
    run_environment = arn[last_index:]
    # runEnvironment = 'test'
    last_updated_by = event['updatedBy']
    user_id = event['id']
    tam_id = event['tamId']
    first_name = event['firstName']
    last_name = event['lastName']
    is_admin = event['admin']
    org_id = event['orgId']
    department_id = event['department_id']
    is_active = event['is_active']
    db_host = os.environ.get("DATABASE_HOST")
    ssm.get_parameter(Name='/mfoneview/' + run_environment + '/usrmgmt/dbhost', WithDecryption=True)['Parameter'][
        'Value']
    db_user_id = \
        ssm.get_parameter(Name='/mfoneview/' + run_environment + '/usrmgmt/user-name', WithDecryption=True)['Parameter'][
            'Value']
    password = os.environ.get("DATABASE_PASSWORD")
    dbname = os.environ.get("DATABASE_NAME")
    ssm.get_parameter(Name='/mfoneview/' + run_environment + '/usrmgmt/dbname', WithDecryption=True)['Parameter'][
        'Value']
    try:
        conn = pymysql.connect(host=db_host, user=db_user_id,
                               passwd=password, db=dbname, connect_timeout=50)
        cur = conn.cursor()
        query = """ UPDATE User set org_id = %s, fname = %s, lname = %s, last_updated_by = %s,
        is_admin = %s, department_id = %s, is_active = %s where User.id = %s"""
        cur.execute(query, (
            org_id, first_name, last_name, str(last_updated_by),
            int(is_admin), department_id, int(is_active), user_id))
        row_count = cur.rowcount
    except Exception as ex:
        logger.error("ERROR: Could not update the User details")
        logger.error(ex)
    finally:
        conn.commit()
        cur.close()
        conn.close()
    if row_count < 0:
        return {
            'statusCode': 500,
            'body': json.dumps("Error: Something went wrong while updating the User details")
        }
    else:
        return {
            'statusCode': 200,
            'body': json.dumps('Details saved successfully')
        }
