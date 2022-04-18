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


class ObjectEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


def lambda_handler(event, context):
    success = True
    department_id = event['id']
    arn = context.invoked_function_arn
    last_index = arn.rindex(':') + 1
    run_environment = arn[last_index:]
    db_host = os.environ.get("DATABASE_HOST")
    user_id = os.environ.get("DATABASE_USERNAME")
    password = os.environ.get("DATABASE_PASSWORD")
    dbname = os.environ.get("DATABASE_NAME")
    records = []
    try:
        conn = pymysql.connect(host=db_host, user=user_id,
                               passwd=password, db=dbname, connect_timeout=50)
        select_query = """SELECT Departments.id, Departments.name,Departments.function, Departments.phone_number,
        Departments.email_id, a.fname, a.lname, b.fname, b.lname, a.id, b.id,
        Departments.organization_id, Departments.default
        FROM Departments, User a, User b
        WHERE Departments.primary_admin = a.id and Departments.backup_admin = b.id
        AND Departments.id = %s;
        """
        cur = conn.cursor()
        cur.execute(select_query, department_id)
        records = cur.fetchall()
    except Exception as ex:
        logger.error("ERROR: Could not retrieve Department with id " + str(department_id))
        logger.error(ex)
        success = False
    department_object = DepartmentObject()
    if len(records) > 0:
        department_record = records[0]
        department_object.id = department_record[0]
        department_object.name = department_record[1]
        department_object.function = department_record[2]
        department_object.phone = department_record[3]
        department_object.email = department_record[4]
        department_object.primary_admin_name = department_record[5] + ' ' + department_record[6]
        department_object.backup_admin_name = department_record[7] + ' ' + department_record[8]
        department_object.primary_admin_id = department_record[9]
        department_object.backup_admin_id = department_record[10]
        department_object.org_id = department_record[11]
        department_object.is_default = department_record[12]
        department_object.returnCode = 200
    else:
        department_object.returnCode = 400
        department_object.errorMessage = 'Department not found'
    return json.loads(json.dumps(department_object, cls=ObjectEncoder))
