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
    lastIndex = arn.rindex(':') + 1
    runEnvironment = arn[lastIndex:]
    # runEnvironment = 'test'
    token_url = ssm.get_parameter(Name='/mfoneview/' + runEnvironment + '/token-url', WithDecryption=True)['Parameter'][
        'Value']
    client_id = event['client_id']
    if 'client_secret' in event:
        client_secret = event['client_secret']
    else:
        client_secret = \
            ssm.get_parameter(Name='/mfoneview/' + runEnvironment + '/sso-client-secret', WithDecryption=True)[
                'Parameter'][
                'Value']

    grant_type = event['grant_type']
    code = event['code']
    redirect_uri = event['redirect_uri']
    if grant_type == 'authorization_code':
        data = {'grant_type': grant_type, 'code': code, 'redirect_uri': redirect_uri, 'client_id': client_id,
                'client_secret': client_secret}
    if grant_type == 'refresh_token':
        refresh_token = event['refresh_token']
        data = {'grant_type': grant_type, 'refresh_token': refresh_token, 'client_id': client_id,
                'client_secret': client_secret}
    access_token_response = requests.post(token_url, data=data)
    tokens = json.loads(access_token_response.text)
    if 'expires' in access_token_response.text:
        if insert_token_record(tokens['access_token'], runEnvironment) > 0:
            return tokens
        else:
            logger.error('Could not insert token data')
            return {'access_token': None}
    else:
        logger.error(access_token_response.text)
        logger.error('Did not receive the token')
        return {'access_token': None}
