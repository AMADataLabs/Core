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


class UserObjectDictionary:
    pass


class UsersListDictionary:
    pass


class ObjectEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


def lambda_handler(event, context):
    org_id = event['orgId']
    arn = context.invoked_function_arn
    last_index = arn.rindex(':') + 1
    run_environment = arn[last_index:]
    query_string = """SELECT User.id, User.fname, User.lname, User.user_name
        FROM User
        WHERE User.org_id = {}
        OR User.is_super_admin = True"""

    list_users = []
    db_host = os.environ.get("DATABASE_HOST")
    user_id = os.environ.get("DATABASE_USERNAME")
    password = os.environ.get("DATABASE_PASSWORD")
    dbname = os.environ.get("DATABASE_NAME")
    try:
        conn = pymysql.connect(host=db_host, user=user_id,
                               passwd=password, db=dbname, connect_timeout=50)
        cur = conn.cursor()
        cur.execute(query_string.format(org_id))
        data_records = cur.fetchall()
        for row in data_records:
            userobj = UserObjectDictionary()
            userobj.id = row[0]
            userobj.name = row[1] + ' ' + row[2]
            userobj.user_name = row[3]
            list_users.append(userobj)
    except Exception as ex:
        logger.error("ERROR: Unexpected error: Could not retrieve list of Users.")
        logger.error(ex)
    finally:
        conn.close()
    return_obj = UsersListDictionary()
    if len(list_users) > 0:
        return_obj.numOfRecords = len(list_users)
        return_obj.usersList = list_users
        return_obj.returnCode = 200
    else:
        return_obj.numOfRecords = 0
        return_obj.usersList = []
        return_obj.returnCode = 400
        return_obj.errMessage = "No users found !"

    return json.loads(json.dumps(return_obj, cls=ObjectEncoder))
