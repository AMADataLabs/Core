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


def remove_current_exclusions(conn, profile_id):
    success = True
    delete_query = "Delete from Groups_Resources where group_id = %s"
    try:
        cur = conn.cursor()
        cur.execute(delete_query, profile_id)
    except Exception as ex:
        logger.error("Error: Current Exclusions could not be removed")
        logger.error(ex)
        success = False
    return success


def process_permissions(conn, profile_id):
    success = True
    if remove_current_exclusions(conn, profile_id):
        logger.info('Current exclusions removed for profile ' + str(profile_id))
    else:
        logger.error('There was an error while removing current exclusions for profile ' + str(profile_id))
        success = False
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
            logger.error("Error: Exclusion could not be assigned to the Profile")
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


def get_default_profile_id(conn, org_id):
    default_profile_ids = []
    try:
        cur = conn.cursor()
        select_query = '''SELECT Groups.id FROM Groups WHERE Groups.organization_id = %s AND Groups.default = %s'''
        cur.execute(select_query, (org_id, True))
        records = cur.fetchall()
        for record in records:
            default_profile_ids.append(record[0])
    except Exception as ex:
        logger.error("Error: Could not retrieve list of default profiles for org " + str(org_id))
        logger.error(ex)

    return default_profile_ids


def reset_default_profiles(conn, org_id):
    success = True
    default_profiles = get_default_profile_id(conn, org_id)
    update_query = ''' UPDATE Groups set Groups.default = %s WHERE Groups.id = %s '''
    for profile_id in default_profiles:
        try:
            cur = conn.cursor()
            cur.execute(update_query, (False, profile_id))
            if cur.rowcount != 1:
                raise Exception('Could not update profile ' + str(profile_id))
        except Exception as ex:
            logger.error('Could not update profile ' + str(profile_id))
            logger.error(ex)
            success = False
    return success


def get_org_users(conn, organization_id):
    org_users = []
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

    return org_users


def get_users_to_be_added(user_id_list, all_org_users):
    users_to_be_added = []
    for user in all_org_users:
        if user not in user_id_list:
            users_to_be_added.append(user)

    return users_to_be_added


def remove_users_of_group(conn, profile_id):
    success = True
    try:
        cur = conn.cursor()
        delete_query = '''DELETE FROM User_Group_Assignment WHERE User_Group_Assignment.group_id = %s'''
        cur.execute(delete_query, profile_id)
    except Exception as ex:
        logger.error("Error: Could not remove users belonging to profile " + str(profile_id))
        logger.error(ex)
        success = False
    return success


def lambda_handler(event, context):
    arn = context.invoked_function_arn
    last_index = arn.rindex(':') + 1
    run_environment = arn[last_index:]
    profile_id = event['id']
    profile_name = event['name']
    permissions = event['permissions']
    new_defult_status = event['is_default']
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
        global excluded_permissions
        excluded_permissions = []
        get_excluded_permissions(conn, permissions)
        if process_permissions(conn, profile_id):
            logger.info("Exclusions have been updated for profile " + profile_name)
        else:
            raise Exception("Error: Exclusions could not be updated for Profile " + profile_name)
        profile_object = get_profile_details(conn, profile_id)
        user_id_list = get_users_of_profile(conn, profile_id)
        if not profile_object.__getattribute__("default"):  # Current default status is False
            if new_defult_status:  # Profile is being made default for the org
                all_org_users = get_org_users(conn, profile_object.__getattribute__("organization_id"))
                users_to_be_added = get_users_to_be_added(user_id_list, all_org_users)
                if assign_profile_to_users(conn, users_to_be_added, profile_id):
                    logger.info('Users have been added to profile id ' + str(profile_id))
                else:
                    logger.error('There was an error while assigning this profile to all users. ')
                    error_message = 'There was an error while assigning this profile to all users. '
                    success = False
                if reset_default_profiles(conn, profile_object.__getattribute__("organization_id")):
                    logger.info('Default profiles for org ' + str(profile_object.__getattribute__("organization_id"))
                                + ' have been reset')
                else:
                    error_message = error_message + 'There was an error while attempting to reset other profiles ' \
                                                    'of this org '
                    logger.error('There was an error while attempting to reset other profiles of this org ')
                    success = False
        else: # Current default status is True
            if not new_defult_status:  # Profile is being made non-default
                default_profiles = get_default_profile_id(conn, profile_object.__getattribute__("organization_id"))
                if len(default_profiles) > 0:
                    success = False
                    error_message = error_message + 'Please assign another profile as default so that this profile' \
                                                    ' will become non-default. '

        if success:
            update_query = '''UPDATE Groups set Groups.name = %s, Groups.default = %s WHERE Groups.id = %s'''
            cur.execute(update_query, (profile_name, int(new_defult_status), profile_id))
            conn.commit()
    except Exception as ex:
        logger.error("ERROR: Could not update Profile")
        logger.error(ex)
        error_message = error_message + "Could not update Profile"
        success = False
    finally:
        cur.close()
        conn.close()

    if success:
        return {
            'statusCode': 200,
            'body': 'Profile updated Successfully'
        }
    else:
        return {
            'statusCode': 500,
            'body': error_message
        }
