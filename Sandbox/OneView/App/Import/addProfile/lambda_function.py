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


class groupObject_Dict:
    pass


class ObjectEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


def check_exclusions(permission):
    if not permission.__getitem__("checked"):
        excluded_permissions.append(permission.__getitem__("id"))
    for child_permission in permission.__getitem__("subresources"):
        check_exclusions(child_permission)


def get_excluded_permissions(conn, permissions):
    for permission in permissions:
        check_exclusions(permission)


def process_permissions(conn, profile_id):
    success = True
    for excluded_permission in excluded_permissions:
        try:
            cur = conn.cursor()
            insert_query = '''INSERT INTO Groups_Resources (group_id, resource_id, access_id)
                        VALUES ( %s, %s, %s)'''
            exclusion_level = '2'
            cur.execute(insert_query, (profile_id, excluded_permission, exclusion_level))
            if cur.rowcount < 1:
                raise Exception("Error: Exclusion could not be assigned to the Profile")
        except Exception as ex:
            logger.error("Error: Unable to assign exclusion to the Profile ")
            logger.error(ex)
            success = False

    return success


def get_profile_details(conn, profile_id):
    group_object = groupObject_Dict()

    default_status = None
    try:
        cur = conn.cursor()
        insert_query = '''  SELECT Groups.id, Groups.name, Groups.department_id, Groups.organization_id, Groups.default
                            FROM Groups
                            WHERE Groups.id = %s
                        '''
        cur.execute(insert_query, profile_id)
        if cur.rowcount < 1:
            raise Exception("Error: Could not retrieve default status of profile " + str(profile_id))
        else:
            records = cur.fetchone()
            group_object.id = records[0]
            group_object.name = records[1]
            group_object.department_id = records[2]
            group_object.organization_id = records[3]
            group_object.default = records[4]
    except Exception as ex:
        logger.error("Error: Could not retrieve default status of profile " + str(profile_id))
        logger.error(ex)

    return group_object


def get_users_of_profile(conn, profile_id):
    list_of_users = []
    try:
        cur = conn.cursor()
        select_query = '''SELECT User_Group_Assignment.user_id FROM User_Group_Assignment
         WHERE User_Group_Assignment.group_id = %s'''
        cur.execute(select_query, profile_id)
        records = cur.fetchall()
        for record in records:
            list_of_users.append(record[0])
    except Exception as ex:
        logger.error("Error: Could not retrieve users belonging to profile " + str(profile_id))
        logger.error(ex)

    return list_of_users


def get_default_profile_id(conn, org_id, profile_id):
    default_profile_ids = []
    try:
        cur = conn.cursor()
        select_query = '''SELECT Groups.id FROM Groups WHERE Groups.organization_id = %s AND Groups.default = %s AND Groups.id != %s '''
        cur.execute(select_query, (org_id, True, profile_id))
        records = cur.fetchall()
        for record in records:
            default_profile_ids.append(record[0])
    except Exception as ex:
        logger.error("Error: Could not retrieve list of default profiles for org " + str(org_id))
        logger.error(ex)

    return default_profile_ids


def reset_default_profiles(conn, org_id, profile_id):
    success = True
    default_profiles = get_default_profile_id(conn, org_id, profile_id)
    update_query = ''' UPDATE Groups set Groups.default = %s WHERE Groups.id = %s '''
    for profile_id in default_profiles:
        try:
            cur = conn.cursor()
            cur.execute(update_query, (False, profile_id))
            if cur.rowcount != 1:
                raise Exception('Could not update profile ' + str(profile_id))
            print(str(cur.rowcount) + ' profiles have been reset')
        except Exception as ex:
            logger.error('Could not update profile ' + str(profile_id))
            logger.error(ex)
            success = False
    return success


def get_org_users(conn, organization_id):
    org_users = []
    success = True
    try:
        cur = conn.cursor()
        select_query = '''SELECT User.id FROM User WHERE User.org_id = %s'''
        cur.execute(select_query, organization_id)
        records = cur.fetchall()
        for record in records:
            org_users.append(record[0])
    except Exception as ex:
        logger.error("Error: Could not retrieve users belonging to org " + str(organization_id))
        logger.error(ex)
        success = False
    logger.info('users of this org are ' + str(org_users))
    return org_users, success


def profile_exists(conn, org_name):
    try:
        cur = conn.cursor()
        query = 'Select id from Groups where name = %s'
        cur.execute(query, org_name)
        records = cur.fetchall()
        if len(records) > 0:
            return True, ''
        else:
            return False, ''
    except Exception as ex:
        logger.error("ERROR: Could not check if Profile Exists")
        logger.error(ex)
        return True, 'ERROR: Unable to check if Profile Exists'


def get_users_to_be_added(user_id_list, all_org_users):
    users_to_be_added = []
    for user in all_org_users:
        if user not in user_id_list:
            users_to_be_added.append(user)

    return users_to_be_added


def assign_profile_to_users(conn, users_to_be_added, profile_id):
    success = True
    insert_query = '''INSERT INTO User_Group_Assignment (user_id, group_id) VALUES (%s, %s)'''
    for user in users_to_be_added:
        try:
            cur = conn.cursor()
            exclusion_level = '2'
            cur.execute(insert_query, (user, profile_id))
            if cur.rowcount < 1:
                raise Exception("Error: User " + str(user) + " could not be assigned to Profile " + str(profile_id))
        except Exception as ex:
            logger.error("Error: User " + str(user) + " could not be assigned to Profile" + str(profile_id))
            logger.error(ex)
            success = False

    return success


def lambda_handler(event, context):
    arn = context.invoked_function_arn
    last_index = arn.rindex(':') + 1
    run_environment = arn[last_index:]
    profile_name = event['name']
    permissions = event['permissions']
    department_id = event['department_id']
    organization_id = event['organization_id']
    default_status = event['is_default']
    success = True
    db_host = os.environ.get("DATABASE_HOST")
    user_id = os.environ.get("DATABASE_USERNAME")
    password = os.environ.get("DATABASE_PASSWORD")
    dbname = os.environ.get("DATABASE_NAME")
    error_message = ''
    try:
        conn = pymysql.connect(host=db_host, user=user_id,
                               passwd=password, db=dbname, connect_timeout=50)
        cur = conn.cursor()
        profile_exists_flag, profile_check_error = profile_exists(conn, profile_name)
        if profile_exists_flag:
            if len(profile_check_error):
                error_message = profile_check_error
            else:
                error_message = "Profile already exists"
                success = False
        else:
            global excluded_permissions
            excluded_permissions = []
            get_excluded_permissions(conn, permissions)
            insert_query = '''INSERT INTO Groups (Groups.name, Groups.department_id, Groups.organization_id, Groups.default)
            VALUES ( %s, %s, %s, %s)'''
            cur.execute(insert_query, (profile_name, department_id, organization_id, int(default_status)))
            if cur.rowcount < 1:
                raise Exception("Error: Profile could not be added")
                success = False
            else:
                profile_id = cur.lastrowid
            if success:
                if process_permissions(conn, profile_id):
                    logger.info("Exclusions have been assigned to the Profile " + profile_name)
                else:
                    raise Exception("Error: Exclusions could not be assigned to the Profile " + profile_name)
                    success = False
            if success:
                if default_status: #new profile is supposed to be default profile for the org
                    all_org_users, all_org_users_success = get_org_users(conn, organization_id)
                    if all_org_users_success:
                        if assign_profile_to_users(conn, all_org_users, profile_id):
                            logger.info('Users have been added to profile id ' + str(profile_id))
                        else:
                            logger.error('There was an error while assigning this profile to all users. ')
                            error_message = 'There was an error while assigning this profile to all users. '
                            success = False
                        if success:
                            if reset_default_profiles(conn, organization_id, profile_id):
                                logger.info('Default profiles for org ' + str(organization_id)
                                            + ' have been reset')
                            else:
                                error_message = error_message + ' There was an error while attempting to reset ' \
                                                                'other profiles of this org '
                                logger.error('There was an error while attempting to reset other profiles of this org ')
                                success = False
                    else:
                        logger.error('There was an error while retrieving all users of the org')
                        success = False
        if success:
            conn.commit()
        else:
            conn.rollback()
    except Exception as ex:
        logger.error("ERROR: Could not add Profile")
        logger.error(ex)
    finally:
        cur.close()
        conn.close()

    if success:
        return {
            'statusCode': 200,
            'body': 'Profile added Successfully'
        }
    else:
        return {
            'statusCode': 500,
            'body': error_message
        }
