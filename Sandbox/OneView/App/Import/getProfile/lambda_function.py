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


class ProfileObject:
    pass


class ResourceObject(dict):
    def __init__(self):
        self = dict()

    def add(self, key, value):
        self[key] = value


class ObjectEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


def get_profile_permissions(conn, records):
    pass


def check_resource_object(existing_resource, resource):
    if existing_resource.__getitem__("id") == resource:
        existing_resource.add("checked", False)
    else:
        for child_resource in existing_resource.__getitem__('subresources'):
            check_resource_object(child_resource, resource)


def add_resource_object(existing_resource, resource):
    if existing_resource.__getitem__("id") == resource[2]:
        resource_object = ResourceObject()
        resource_object.add("id", resource[0])
        resource_object.add("checked", True)
        resource_object.add("name", resource[1])
        resource_object.add("ui_name", resource[3])
        resource_object.add("subresources", [])
        existing_resource.__getitem__("subresources").append(resource_object)
        return True
    else:
        for child_resource in existing_resource.__getitem__('subresources'):
            add_resource_object(child_resource, resource)


def create_resource_list(records):
    resource_list = []
    for resource in records:
        if resource[2] is None:
            resource_object = ResourceObject()
            resource_object.add("id", resource[0])
            resource_object.add("checked", True)
            resource_object.add("name", resource[1])
            resource_object.add("ui_name", resource[3])
            resource_object.add("subresources", [])
            resource_list.append(resource_object)
        else:
            for existing_resource in resource_list:
                add_resource_object(existing_resource, resource)
    return resource_list


def set_exclusions(resource_id, profile_object):
    for permission in profile_object.permissions:
        check_resource_object(permission, resource_id)


def get_resource_list(conn):
    resource_list = []

    try:
        select_query = """SELECT id, name, parent_resource_id, ui_name FROM Resource order by parent_resource_id"""
        cur = conn.cursor()
        cur.execute(select_query)
        records = cur.fetchall()
        if len(records) > 0:
            resource_list = create_resource_list(records)
        else:
            logger.error("ERROR: No records found while retrieving a list of Resources")
    except Exception as ex:
        logger.error("ERROR: Could not retrieve list of resources")
        logger.error(ex)

    return resource_list


def lambda_handler(event, context):
    success = True
    profile_id = event['id']
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
        select_query = """SELECT groups.name, gr.resource_id, groups.department_id, groups.organization_id,
        groups.default
        FROM Groups groups
        LEFT JOIN
        (SELECT Groups_Resources.group_id , Resource.id AS resource_id
        FROM Groups_Resources, Resource
        WHERE Groups_Resources.resource_id = Resource.id) gr
        ON groups.id = gr.group_id WHERE groups.id = %s
        """
        cur = conn.cursor()
        cur.execute(select_query, profile_id)
        records = cur.fetchall()
    except Exception as ex:
        logger.error("ERROR: Could not retrieve Group with id " + str(profile_id))
        logger.error(ex)
        success = False
    profile_object = ProfileObject()
    if len(records) > 0:
        profile_object.id = profile_id
        profile_object.name = records[0][0]
        profile_object.department_id = records[0][2]
        profile_object.organization_id = records[0][3]
        profile_object.is_default = records[0][4]
        profile_object.permissions = get_resource_list(conn)
        for record in records:
            set_exclusions(record[1], profile_object)
        profile_object.returnCode = 200
    else:
        profile_object.returnCode = 400
        profile_object.errorMessage = 'Profile not found'
    return json.loads(json.dumps(profile_object, cls=ObjectEncoder))
