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
    department_id = event['department_id']
    include_admins = event['includeAdmins']
    is_super = event['superAdmin']
    page_num = "1"
    off_set = 0
    page_size = "10"
    search_text = ""
    if 'pageSize' in event:
        page_size = event['pageSize']
    if 'pageNumber' in event:
        page_num = event['pageNumber']
        if page_num == "1":
            off_set = 0
        else:
            off_set = (int(page_num) - 1) * int(page_size)
    if 'search' in event:
        search_text = event['search']
    arn = context.invoked_function_arn
    last_index = arn.rindex(':') + 1
    run_environment = arn[last_index:]
    query_string = """SELECT User.tam_id, User.fname, User.mname, User.lname, User.email, User.is_admin,
        User.user_name,User.is_active, User.org_id, Organization.name, User.id, Departments.name, Departments.id
        from Organization, User, Departments
        where User.org_id = Organization.id and Departments.organization_id = Organization.id
        and User.department_id = Departments.id """
    query_count_string = """SELECT count(*) from User, Organization, Departments where User.org_id = Organization.id
      and Departments.organization_id = Organization.id
      and User.department_id = Departments.id """

    if len(search_text) > 0:
        search_clause = ' and (User.fname like \'%' + search_text + '%\' or User.lname like \'%' + search_text + \
                        '%\' or User.user_name like \'%' + search_text + '%\' or User.email like \'%' + search_text + \
                        '%\')'
        query_string = query_string + search_clause
        query_count_string = query_count_string + search_clause
    if include_admins == False:
        admin_clause = ' and User.is_admin = false '
        query_string = query_string + admin_clause
        query_count_string = query_count_string + admin_clause
    org_clause = ' and Organization.id = {}'
    department_clause = ' and Departments.id = {}'
    list_users = []
    number_of_records = 0
    db_host = os.environ.get("DATABASE_HOST")
    user_id = os.environ.get("DATABASE_USERNAME")
    password = os.environ.get("DATABASE_PASSWORD")
    dbname = os.environ.get("DATABASE_NAME")
    try:
        conn = pymysql.connect(host=db_host, user=user_id,
                               passwd=password, db=dbname, connect_timeout=50)
        cur = conn.cursor()
        if is_super:
            if org_id != "-1":
                if department_id != "-1":
                    query_string = query_string + org_clause + department_clause
                    query_count_string = query_count_string + org_clause + department_clause
                    cur.execute(query_count_string.format(org_id, department_id))
                else:
                    query_string = query_string + org_clause
                    query_count_string = query_count_string + org_clause
                    cur.execute(query_count_string.format(org_id))
            else:
                cur.execute(query_count_string)
        else:
            if department_id != "-1":
                query_string = query_string + org_clause + department_clause
                query_count_string = query_count_string + org_clause + department_clause
                cur.execute(query_count_string.format(org_id, department_id))
            else:
                query_string = query_string + org_clause
                query_count_string = query_count_string + org_clause
                cur.execute(query_count_string.format(org_id))
        all_records = cur.fetchall()
        count_row = all_records[0]
        if count_row[0] > 0:
            number_of_records = count_row[0]
            if count_row[0] > int(page_size):
                query_string = query_string + ' limit ' + str(page_size) + ' offset ' + str(off_set)
            if org_id != "-1":
                if department_id != "-1":
                    cur.execute(query_string.format(org_id, department_id))
                else:
                    cur.execute(query_string.format(org_id))
            else:
                cur.execute(query_string)
            data_records = cur.fetchall()
            for row in data_records:
                userobj = UserObjectDictionary()
                userobj.tamId = row[0]
                userobj.fname = row[1]
                userobj.middleName = row[2]
                userobj.lname = row[3]
                userobj.name = userobj.fname + ' ' + userobj.lname
                userobj.email = row[4]
                userobj.admin = row[5]
                userobj.userName = row[6]
                userobj.is_active = row[7]
                userobj.orgId = row[8]
                userobj.orgName = row[9]
                userobj.id = row[10]
                userobj.departmentName = row[11]
                userobj.department_id = row[12]
                list_users.append(userobj)
    except Exception as ex:
        logger.error("ERROR: Unexpected error: Could not retrieve list of Users.")
        logger.error(ex)
    finally:
        conn.close()
    return_obj = UsersListDictionary()
    if number_of_records > 0:
        return_obj.numOfRecords = number_of_records
        return_obj.usersList = list_users
        return_obj.returnCode = 200
    else:
        return_obj.numOfRecords = 0
        return_obj.usersList = []
        return_obj.returnCode = 400
        return_obj.errMessage = "No users found for this Organization and Department!"

    return json.loads(json.dumps(return_obj, cls=ObjectEncoder))
