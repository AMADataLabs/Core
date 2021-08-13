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


class ProfileObjectDictionary(dict):
    def __init__(self):
        self = dict()

    def add(self, key, value):
        self[key] = value


class ProfilesListDictionary:
    pass


class ObjectEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


def lambda_handler(event, context):
    org_id = event['org_id']
    department_id = event['department_id']
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
    query_string = """SELECT groups.id, groups.name, IFNULL(gr.resource_name, 'No Exclusions'),
    groups.default
    FROM Groups groups
    LEFT JOIN
    (SELECT Groups_Resources.group_id , Resource.name AS resource_name
    FROM Groups_Resources, Resource WHERE Groups_Resources.resource_id = Resource.id) gr
    ON groups.id = gr.group_id """

    query_count_string = """SELECT count(*)
    FROM Groups groups
    LEFT JOIN
    (SELECT Groups_Resources.group_id , Resource.name AS resource_name
    FROM Groups_Resources, Resource WHERE Groups_Resources.resource_id = Resource.id) gr
    ON groups.id = gr.group_id """

    if len(search_text) > 0:
        search_clause = ' and (Groups.name like \'%' + search_text + '%\' or Resource.name like \'%' + search_text + \
                        '%\')'
        query_string = query_string + search_clause
        query_count_string = query_count_string + search_clause
    org_clause = ' WHERE groups.organization_id = {}'
    department_clause = ' AND groups.department_id = {}'
    list_users = []
    number_of_records = 0
    db_host = os.environ.get("DATABASE_HOST")
    user_id = os.environ.get("DATABASE_USERNAME")
    password = os.environ.get("DATABASE_PASSWORD")
    dbname = os.environ.get("DATABASE_NAME")
    return_obj = ProfilesListDictionary()
    return_obj.profiles = []
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
            # if count_row[0] > int(page_size):
            #     query_string = query_string + ' limit ' + str(page_size) + ' offset ' + str(off_set)
            if org_id != "-1":
                if department_id != "-1":
                    cur.execute(query_string.format(org_id, department_id))
                else:
                    cur.execute(query_string.format(org_id))
            else:
                cur.execute(query_string)
            data_records = cur.fetchall()
            profile_object = None
            previous_group_id = ''
            for row in data_records:
                if row[0] != previous_group_id:  # New Profile encountered
                    if previous_group_id != '':
                        return_obj.profiles.append(profile_object)
                    previous_group_id = row[0]
                    profile_object = ProfileObjectDictionary()
                    profile_object.add('exclusions', [])
                    profile_object.add("name", row[1])
                    profile_object.add("id", row[0])
                    profile_object.add("is_default", row[3])
                profile_object.__getitem__("exclusions").append(row[2])
    except Exception as ex:
        logger.error("ERROR: Unexpected error: Could not retrieve list of Profiles.")
        logger.error(ex)
    finally:
        conn.close()
    if number_of_records > 0:
        if profile_object is not None:
            return_obj.profiles.append(profile_object)
        return_obj.numOfRecords = number_of_records
        return_obj.returnCode = 200
    else:
        return_obj.numOfRecords = 0
        return_obj.returnCode = 400
        return_obj.errMessage = "No profiles found for this Organization and Department!"

    return json.loads(json.dumps(return_obj, cls=ObjectEncoder))
