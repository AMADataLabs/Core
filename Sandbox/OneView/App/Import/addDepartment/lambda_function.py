import logging
import os
from json import JSONEncoder

import boto3
import pymysql

port = 3306
logger = logging.getLogger()
logger.setLevel(logging.INFO)
ssm = boto3.client('ssm', region_name=os.environ['AWS_REGION'])


class ObjectEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


def assign_department_to_users(conn, current_department_id, new_department_id):
    logger.info('current default dept id is ' + str(current_department_id))
    logger.info('new default dept id is ' + str(new_department_id))
    success = True
    try:
        cur = conn.cursor()
        update_query = '''
                        UPDATE User set User.department_id = %s WHERE User.department_id = %s
                        '''
        cur.execute(update_query, (new_department_id, current_department_id))
        logger.info(str(cur.rowcount) + ' users have been updated with new department id')
    except Exception as ex:
        logger.error("Error: Could not update users department to " + str(new_department_id))
        logger.error(ex)
        success = False

    return success


def department_exists(conn, department_name, org_id):
    try:
        cur = conn.cursor()
        query = 'SELECT Departments.id FROM Departments WHERE Departments.name = %s' \
                ' AND Departments.organization_id = %s'
        cur.execute(query, (department_name, org_id))
        records = cur.fetchall()
        if len(records) > 0:
            return True, ''
        else:
            return False, ''
    except Exception as ex:
        logger.error("ERROR: Could not check if Department exists")
        logger.error(ex)
        return True, 'ERROR: Unable to check if Department Exists'


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


def reset_previous_default_department(conn, previous_default_department):
    success = True
    try:
        cur = conn.cursor()
        update_query = ''' UPDATE Departments set Departments.default = %s WHERE Departments.id = %s '''
        cur.execute(update_query, (False, previous_default_department))
    except Exception as ex:
        logger.error("Error: Could not update default status of department " + str(previous_default_department))
        logger.error(ex)
        success = False

    return success


def get_previous_default_department(conn, org_id):
    previous_default_department = None
    error_message = ''
    try:
        cur = conn.cursor()
        select_query = '''SELECT Departments.id FROM Departments WHERE Departments.organization_id = %s
                        AND Departments.default = %s '''
        cur.execute(select_query, (org_id, True))
        records = cur.fetchall()
        if len(records) > 0:
            previous_default_department = records[0][0]
    except Exception as ex:
        logger.error("Error: Could not retrieve current default department for org " + str(org_id))
        logger.error(ex)
        error_message = "Could not retrieve current default department for org " + str(org_id)
    return previous_default_department, error_message


def lambda_handler(event, context):

    arn = context.invoked_function_arn
    last_index = arn.rindex(':') + 1
    run_environment = arn[last_index:]
    department_name = event['name']
    department_function = event['function']
    primary_admin = event['primary']
    backup_admin = event['backup']
    org_id = event['orgId']
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
        department_exists_flag, department_check_error = department_exists(conn, department_name, org_id)
        if department_exists_flag:
            if len(department_check_error):
                error_message = department_check_error
            else:
                error_message = "Department already exists for this Organization"
                success = False
        else:
            insert_query = '''INSERT INTO Departments (Departments.name, Departments.organization_id,
                            Departments.primary_admin, Departments.function, Departments.backup_admin,
                            Departments.default)
                            VALUES ( %s, %s, %s, %s, %s, %s)'''
            cur.execute(insert_query, (department_name, org_id, primary_admin, department_function,
                                       backup_admin, int(default_status)))
            if cur.rowcount < 1:
                raise Exception("Error: Department could not be added")
                success = False
            else:
                department_id = cur.lastrowid
            if success:
                if default_status:  # New department is default for the org
                    previous_default_department, previous_default_department_error = \
                        get_previous_default_department(conn, org_id)
                    if previous_default_department:
                        if reset_previous_default_department(conn, previous_default_department):
                            logger.info('Previous default department for org ' + str(org_id) + ' has been reset')
                        else:
                            logger.error('Error: There was an error resetting the previous default department')
                            error_message = error_message = "There was an error resetting the previous " \
                                                            "default department"
                            success = False
                        if success:
                            if assign_department_to_users(conn, previous_default_department, department_id):
                                logger.info(
                                    "Users have been assigned to the new default department " + str(department_id))
                            else:
                                success = False
                                raise Exception(
                                    "Error: There was an error while assigning new default department to users")
                    else:
                        error_message = error_message + previous_default_department_error
                        success = False
        if success:
            conn.commit()
    except Exception as ex:
        logger.error("ERROR: Could not add Department " + department_name)
        logger.error(ex)
        success = False
    finally:
        cur.close()
        conn.close()

    if success:
        return {
            'statusCode': 200,
            'body': 'Department added successfully'
        }
    else:
        return {
            'statusCode': 500,
            'body': error_message
        }
