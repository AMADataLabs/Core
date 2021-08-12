import json
import logging
import os
from datetime import datetime, timedelta

import boto3
import pymysql
import requests

ssm = boto3.client('ssm', region_name=os.environ['AWS_REGION'])
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_expiry():
    now = datetime.now()
    future = now + timedelta(seconds=3600)


def insert_token_record(token, run_environment):
    logger.error(token)
    db_host = os.environ.get("DATABASE_HOST")
    user_id = os.environ.get("DATABASE_USERNAME")
    password = os.environ.get("DATABASE_PASSWORD")
    dbname = os.environ.get("DATABASE_NAME")

    insert_token_query = 'INSERT INTO Tokens (bearer_token, expiry_time) values (%s, %s)'
    expiry_time = datetime.now() + timedelta(seconds=3590)

    try:
        conn = pymysql.connect(host=db_host, user=user_id,
                               passwd=password, db=dbname, connect_timeout=50)
        cur = conn.cursor()
        cur.execute(insert_token_query, (token, expiry_time))
        row_count = cur.rowcount
        if row_count <= 0:
            raise Exception('Error: Unable to insert token record!!!')
    except Exception as ex:
        logger.error("ERROR: Could not fetch the token")
    finally:
        conn.commit()
        cur.close()
        conn.close()
    return row_count


def lambda_handler(event, context):
    arn = context.invoked_function_arn
    last_index = arn.rindex(':') + 1
    run_environment = arn[last_index:]
    dremio_user_id = \
        ssm.get_parameter(Name='/mfoneview/' + run_environment + '/usrmgmt/dremio_user_id', WithDecryption=True)[
            'Parameter'][
            'Value']
    dremio_password = \
        ssm.get_parameter(Name='/mfoneview/' + run_environment + '/usrmgmt/dremio_password', WithDecryption=True)[
            'Parameter'][
            'Value']
    dremio_url = \
        ssm.get_parameter(Name='/mfoneview/' + run_environment + '/usrmgmt/dremio_url', WithDecryption=True)[
            'Parameter'][
            'Value']

    source_ip = event['sourceIp']
    data = {'userName': dremio_user_id, 'password': dremio_password, 'clientIPAddress': source_ip}
    headers = {'Content-Type': 'application/json'}
    access_token_response = requests.post(dremio_url, data=json.dumps(data), headers=headers)
    if access_token_response.status_code == requests.codes.ok:
        return json.loads(access_token_response.text)
    else:
        logger.error('Error: Not able to retrieve token ' + str(access_token_response))
        return {'token': None}
