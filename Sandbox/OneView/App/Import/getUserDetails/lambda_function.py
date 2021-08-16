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


class userObject_Dict:
    pass


class groupObject_Dict:
    pass


class domainObject_Dict:
    pass


class ObjectEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


def get_domains(conn, user_object):
    domains_query = """SELECT Domains.id, Domains.domain_name from Organization_Domains, Domains
  where Organization_Domains.organization_id = %s and Organization_Domains.domain_id = Domains.id """

    try:
        cur = conn.cursor()
        cur.execute(domains_query, (user_object.orgId))
        records = cur.fetchall()
    except Exception as ex:
        logger.error("ERROR: Unexpected error: Could not retrieve Groups.")
        logger.error(ex)
    if len(records) > 0:
        for row in records:
            domain_obj = domainObject_Dict()
            domain_obj.id = row[0]
            domain_obj.domain_name = row[1]
            user_object.orgDomains.append(domain_obj)


def get_all_inclusions(all_permissions, exclusions):
    inclusions: list = []
    for permission in all_permissions:
        if permission not in exclusions:
            inclusions.append(permission)


def get_all_permissions(conn):
    permissions_query = """SELECT ui_name, parent_resource_id FROM Resource order by parent_resource_id"""
    records: list = []
    try:
        cur = conn.cursor()
        cur.execute(permissions_query)
        records = cur.fetchall()
    except Exception as ex:
        logger.error("ERROR: Unexpected error: Could not retrieve Permissions")
        logger.error(ex)
    if len(records) > 0:
        for row in records:
            all_permissions.append(row[0])


def get_groups(user_object, conn, group_guery_where_string, value_to_be_searched):
    user_object.assignedGroups = []
    groups_query = """SELECT Groups.id, Groups.name from User, User_Group_Assignment, Groups """ + group_guery_where_string
    records: list = []
    try:
        cur = conn.cursor()
        cur.execute(groups_query, (value_to_be_searched))
        records = cur.fetchall()
    except Exception as ex:
        logger.error("ERROR: Unexpected error: Could not retrieve Groups.")
        logger.error(ex)
    if len(records) > 0:
        for row in records:
            group_object = groupObject_Dict()
            group_object.id = row[0]
            group_object.name = row[1]
            user_object.assignedGroups.append(group_object)


def get_exclusions(conn, user_object):
    inclusions: list = []
    exclusions: list = []
    user_object.exclusions = []
    records: list = []
    groups_query = """
                SELECT Resource.ui_name
                FROM
                    Groups_Resources,
                    Resource,
                    Groups
                WHERE
                    Groups.id = %s
                AND Groups.id = Groups_Resources.group_id
                AND Groups_Resources.resource_id = Resource.id;
         """
    if len(user_object.assignedGroups) > 0:
        for group_obj in user_object.assignedGroups:
            try:
                cur = conn.cursor()
                cur.execute(groups_query, group_obj.id)
                records = cur.fetchall()
            except Exception as ex:
                logger.error("ERROR: Unexpected error: Could not retrieve Exclusions.")
                logger.error(ex)
            if len(records) > 0:
                group_exclusions: list = []
                for row in records:
                    group_exclusions.append(row[0])
                logger.info('Exclusions for group ' + str(group_obj.id) + ' are ' + str(group_exclusions))
                for permission in all_permissions: # check ALL Permissions.
                    if permission not in group_exclusions: # If a permission is not excluded, that means it is
                                                  # allowed to be accessed
                        if permission not in inclusions: # ensure that the permission is not already a
                                                         # part of inclusions
                            inclusions.append(permission)
            else:
                for permission in all_permissions:
                    if permission not in inclusions:  # ensure that the permission is not already a
                        # part of inclusions
                        inclusions.append(permission)

        logger.info('Total inclusions are ' + str(inclusions))

        for permission in all_permissions:
            if permission not in inclusions:
                exclusions.append(permission)
        logger.info('Total exclusions are ' + str(exclusions))
    if len(exclusions) == 0:
        if len(user_object.assignedGroups) > 0:
            exclusions.append('No Exclusions')
    user_object.exclusions = exclusions


def lambda_handler(event, context):
    tam_id = event['tamId']
    user_id = event['id']
    arn = context.invoked_function_arn
    last_index = arn.rindex(':') + 1
    run_environment = arn[last_index:]
    records: list = []
    select_query = """SELECT User.id, User.tam_id, User.fname, User.mname, User.lname, User.email, Organization.name,
                User.addr1, User.addr2, User.addr3,
  				User.city, User.zip, User.state, User.phone, User.user_name, User.is_admin, User.royalty_portal_access,
  				Organization.org_size, Organization.about, Organization.main_contact, Organization.industry,
  				Organization.id, User.is_active, User.is_super_admin, User.devportal_access,
  				Organization.type_id, Organization.category_id, Organization.addr1, Organization.addr2,
  				Organization.addr3, Organization.city, Organization.state, Organization.zip,
  				Organization.phone, Organization.country, Organization.source_id, User.department_id
  				FROM User, Organization """
    if user_id:
        where_string = 'where User.id = %s and User.org_id = Organization.id'
        group_query_where_string = 'where User.id = %s and User.id = User_Group_Assignment.user_id and User_Group_Assignment.group_id = Groups.id'
        select_query = select_query + where_string
        value_to_be_searched = user_id
    else:
        where_string = 'where User.tam_id = %s and User.org_id = Organization.id'
        group_query_where_string = 'where User.tam_id = %s and User.id = User_Group_Assignment.user_id and ' \
                                   'User_Group_Assignment.group_id = Groups.id'
        select_query = select_query + where_string
        value_to_be_searched = tam_id

    db_host = os.environ.get("DATABASE_HOST")
    user_id = os.environ.get("DATABASE_USERNAME")
    password = os.environ.get("DATABASE_PASSWORD")
    dbname = os.environ.get("DATABASE_NAME")
    userobj = userObject_Dict()
    try:
        conn = pymysql.connect(host=db_host, user=user_id,
                               passwd=password, db=dbname, connect_timeout=50)
        cur = conn.cursor()
        cur.execute(select_query, (value_to_be_searched))
        records = cur.fetchall()
        global all_permissions
        all_permissions = []
        get_all_permissions(conn)
        if len(records) > 0:
            row = records[0]
            userobj.id = row[0]
            userobj.tamId = row[1]
            userobj.firstName = row[2]
            userobj.middleName = row[3]
            userobj.lastName = row[4]
            userobj.email = row[5]
            userobj.orgName = row[6]
            userobj.addr1 = row[7]
            userobj.addr2 = row[8]
            userobj.addr3 = row[9]
            userobj.city = row[10]
            userobj.zip = row[11]
            userobj.state = row[12]
            userobj.phone = row[13]
            userobj.userName = row[14]
            userobj.admin = row[15]
            userobj.hasrpAccess = row[16]
            userobj.orgSize = row[17]
            userobj.orgAbout = row[18]
            userobj.orgMainContact = row[19]
            userobj.orgIndustry = row[20]
            userobj.orgId = row[21]
            userobj.is_active = row[22]
            userobj.superAdmin = row[23]
            userobj.devportalAccess = row[24]
            userobj.department_id = row[36]
            userobj.orgDomains = []
            get_groups(userobj, conn, group_query_where_string, value_to_be_searched)
            get_domains(conn, userobj)
            get_exclusions(conn, userobj)
            userobj.returnCode = 200
        else:
            userobj.returnCode = 500
            userobj.errMessage = "User not found"
    except Exception as ex:
        logger.error("ERROR: Unexpected error: Could not retrieve details.")
        logger.error(ex)
    finally:
        conn.close()

    return json.loads(json.dumps(userobj, cls=ObjectEncoder))
