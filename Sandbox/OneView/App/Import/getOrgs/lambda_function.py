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


class OrgsListDictionary:
    pass


class OrgObjectDictionary:
    pass


class ObjectEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


def lambda_handler(event, context):
    success = True
    arn = context.invoked_function_arn
    last_index = arn.rindex(':') + 1
    run_environment = arn[last_index:]
    db_host = os.environ.get("DATABASE_HOST")
    user_id = os.environ.get("DATABASE_USERNAME")
    password = os.environ.get("DATABASE_PASSWORD")
    dbname = os.environ.get("DATABASE_NAME")

    try:
        conn = pymysql.connect(host=db_host, user=user_id,
                               passwd=password, db=dbname, connect_timeout=50)
        cur = conn.cursor()
        select_query = """SELECT Organization.id, Organization.name from Organization"""
        cur.execute(select_query)
        records = cur.fetchall()

    except Exception as ex:
        logger.error("ERROR: Could not retrieve list of Organizations")
        logger.error(ex)
        success = False

    list_of_orgs = []
    return_object = OrgsListDictionary()
    if success:
        for row in records:
            org_obj = OrgObjectDictionary()
            org_obj.id = row[0]
            org_obj.name = row[1]
            list_of_orgs.append(org_obj)
            return_object.orgs = list_of_orgs
            return_object.returnCode = 200
    else:
        return_object.orgs = list_of_orgs
        return_object.returnCode = 400
        return_object.errMessage = 'Unable to get list of Organizations'

    return json.loads(json.dumps(return_object, cls=ObjectEncoder))
