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


class GroupUsersObjectDictionary:
    pass


class UserObjectDictionary:
    pass


class ObjectEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


def get_group_details(conn, group_id):
    org_id = None
    group_name = ''
    get_org_id_query = """ Select Groups.organization_id, Groups.name From Groups where Groups.id = %s"""
    try:
        cur = conn.cursor()
        cur.execute(get_org_id_query, group_id)
        records = cur.fetchall()
        if len(records) > 0:
            org_id = records[0][0]
            group_name = records[0][1]
    except Exception as ex:
        logger.error("ERROR: Could not retrieve Organization info for the Group")
        logger.error(ex)
    return org_id, group_name

def lambda_handler(event, context):
    success = True
    arn = context.invoked_function_arn
    last_index = arn.rindex(':') + 1
    group_id = event['group_id']
    run_environment = arn[last_index:]
    db_host = os.environ.get("DATABASE_HOST")
    user_id = os.environ.get("DATABASE_USERNAME")
    password = os.environ.get("DATABASE_PASSWORD")
    dbname = os.environ.get("DATABASE_NAME")
    org_id = None
    try:
        conn = pymysql.connect(host=db_host, user=user_id,
                               passwd=password, db=dbname, connect_timeout=50)
        org_id, group_name = get_group_details(conn, group_id)
        if not org_id:
            raise Exception("Error: There was an error in retrieving organization info of the Group")
        cur = conn.cursor()
        select_query = """SELECT User.id, User.fname, User.lname, User.department_id, Departments.name,
                        User.user_name
                        FROM User, User_Group_Assignment, Departments
                        WHERE User.id = User_Group_Assignment.user_id
                        AND User.department_id = Departments.id
                        AND User_Group_Assignment.group_id = %s"""
        cur.execute(select_query, group_id)
        records = cur.fetchall()

    except Exception as ex:
        logger.error("ERROR: Could not retrieve list of Users")
        logger.error(ex)
        success = False

    list_of_users = []
    return_object = GroupUsersObjectDictionary()
    return_object.org_id = org_id
    return_object.name = group_name
    if success:
        if len(records) > 0:
            for row in records:
                user_obj = UserObjectDictionary()
                user_obj.id = row[0]
                user_obj.name = row[1] + " " + row[2]
                user_obj.department_id = row[3]
                user_obj.department_name = row[4]
                user_obj.user_name = row[5]
                list_of_users.append(user_obj)
            return_object.returnCode = 200
        else:
            return_object.returnCode = 400
            return_object.errMessage = 'No Users assigned to this Group'

    else:
        return_object.returnCode = 500
        return_object.errMessage = 'Unable to get list of Users for the specified Group'
    return_object.users = list_of_users

    return json.loads(json.dumps(return_object, cls=ObjectEncoder))
