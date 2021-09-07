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


class DepartmentObject:
    pass


class DepartmentListObject:
    pass


class ObjectEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


def lambda_handler(event, context):
    org_id = event['orgId']
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
    except Exception as ex:
        logger.error("ERROR: Could not retrieve list of Departments")
        logger.error(ex)
    list_departments = []
    cur = conn.cursor()
    logger.info('now getting departments of org ' + str(org_id))
    select_query = """SELECT Departments.id, Departments.name,
    Departments.function, Departments.phone_number,
    Departments.email_id, a.fname, a.lname, b.fname, b.lname, Departments.default
    FROM Departments, User a, User b
    WHERE Departments.primary_admin = a.id and Departments.backup_admin = b.id """
    org_clause = """    AND Departments.organization_id = %s;    """
    if org_id == '-1':
        cur.execute(select_query)
    else:
        select_query = select_query + org_clause
        cur.execute(select_query, org_id)

    records = cur.fetchall()
    return_object = DepartmentListObject()
    for row in records:
        department_object = DepartmentObject()
        department_object.id = row[0]
        department_object.name = row[1]
        department_object.function = row[2]
        department_object.phone = row[3]
        department_object.email = row[4]
        department_object.primary_admin_name = row[5] + ' ' + row[6]
        department_object.backup_admin_name = row[7] + ' ' + row[8]
        department_object.is_default = row[9]
        list_departments.append(department_object)
    if len(list_departments) > 0:
        return_object.returnCode = 200
        return_object.departments = list_departments
    else:
        return_object.returnCode = 400
        return_object.errorMessage = 'No Departments found'
    return json.loads(json.dumps(return_object, cls=ObjectEncoder))
