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


class ListOfResourcesObject:
    pass


class ResourceObject(dict):
    def __init__(self):
        self = dict()

    def add(self, key, value):
        self[key] = value


class ObjectEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__



def add_resource_object(existing_resource, resource):
    if existing_resource.__getitem__("id") == resource[2]:
        resource_object = ResourceObject()
        resource_object.add("id", resource[0])
        resource_object.add("checked", True)
        resource_object.add("name", resource[1])
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
            resource_object.add("subresources", [])
            resource_list.append(resource_object)
        else:
            for existing_resource in resource_list:
                add_resource_object(existing_resource, resource)
    return resource_list


def get_resource_list(conn):
    resource_list = []

    try:
        select_query = """SELECT id, name, parent_resource_id FROM Resource order by parent_resource_id"""
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
    arn = context.invoked_function_arn
    last_index = arn.rindex(':') + 1
    run_environment = arn[last_index:]
    db_host = os.environ.get("DATABASE_HOST")
    user_id = os.environ.get("DATABASE_USERNAME")
    password = os.environ.get("DATABASE_PASSWORD")
    dbname = os.environ.get("DATABASE_NAME")
    records = []
    profile_object = ListOfResourcesObject()

    try:
        conn = pymysql.connect(host=db_host, user=user_id,
                               passwd=password, db=dbname, connect_timeout=50)

        list_of_resources = get_resource_list(conn)
    except Exception as ex:
        logger.error("ERROR: Could not retrieve Group with id " + str(profile_id))
        logger.error(ex)
        success = False
    if len(list_of_resources) > 0:
        profile_object.permissions = list_of_resources
        profile_object.returnCode = 200
    else:
        profile_object.returnCode = 400
        profile_object.errorMessage = 'Resources not found'
    return json.loads(json.dumps(profile_object, cls=ObjectEncoder))
