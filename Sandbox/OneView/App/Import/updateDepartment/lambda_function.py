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


class department_object_dict:
    pass


def department_exists(conn, department_name, org_id, current_department_id):
    try:
        cur = conn.cursor()
        query = 'SELECT Departments.id FROM Departments WHERE Departments.name = %s' \
                ' AND Departments.organization_id = %s AND Departments.id != %s'
        cur.execute(query, (department_name, org_id, current_department_id))
        records = cur.fetchall()
        if len(records) > 0:
            return True, ''
        else:
            return False, ''
    except Exception as ex:
        logger.error("ERROR: Could not check if Department exists")
        logger.error(ex)
        return True, 'ERROR: Unable to check if Department Exists'


def get_department_details(conn, department_id):
    department_object = department_object_dict()
    default_status = None
    try:
        cur = conn.cursor()
        select_department_query = '''  SELECT Departments.id, Departments.name, Departments.organization_id, Departments.default
                            FROM Departments
                            WHERE Departments.id = %s
                        '''
        cur.execute(select_department_query, department_id)
        if cur.rowcount < 1:
            raise Exception("Error: Could not retrieve default status of profile " + str(department_id))
        else:
            records = cur.fetchone()
            department_object.id = records[0]
            department_object.name = records[1]
            department_object.organization_id = records[2]
            department_object.default = records[3]
    except Exception as ex:
        logger.error("Error: Could not retrieve details of Department " + str(department_id))
        logger.error(ex)

    return department_object


def get_previous_default_department(conn, org_id):
    previous_default_department = None
    error_message = ''
    try:
        cur = conn.cursor()
        select_query = '''SELECT Departments.id FROM Departments WHERE Departments.organization_id = %s
                        AND Departments.default = %s '''
        cur.execute(select_query, (org_id, '1'))
        records = cur.fetchall()
        print('previous default departments are ' + str(records))
        if len(records) > 0:
            previous_default_department = records[0][0]
    except Exception as ex:
        logger.error("Error: Could not retrieve current default department for org " + str(org_id))
        logger.error(ex)
        error_message = "Could not retrieve current default department for org " + str(org_id)
    return previous_default_department, error_message


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


def get_default_department_id(conn, org_id):
    default_department_ids = []
    try:
        cur = conn.cursor()
        select_query = '''SELECT Departments.id FROM Departments WHERE Departments.organization_id = %s
        AND Departments.default = %s'''
        cur.execute(select_query, (org_id, '1'))
        records = cur.fetchall()
        for record in records:
            default_department_ids.append(record[0])
    except Exception as ex:
        logger.error("Error: Could not retrieve list of default departments for org " + str(org_id))
        logger.error(ex)

    return default_department_ids


def lambda_handler(event, context):
    arn = context.invoked_function_arn
    last_index = arn.rindex(':') + 1
    run_environment = arn[last_index:]
    department_name = event['name']
    department_function = event['function']
    primary_admin = event['primary']
    backup_admin = event['backup']
    department_id = event['departmentId']
    default_status = event['is_default']
    success = True
    error_message = ''
    db_host = os.environ.get("DATABASE_HOST")
    user_id = os.environ.get("DATABASE_USERNAME")
    password = os.environ.get("DATABASE_PASSWORD")
    dbname = os.environ.get("DATABASE_NAME")
    row_count = -1

    try:
        conn = pymysql.connect(host=db_host, user=user_id,
                               passwd=password, db=dbname, connect_timeout=50)
        cur = conn.cursor()
        department_object = get_department_details(conn, department_id)
        department_exists_flag, department_check_error = \
            department_exists(conn, department_name, department_object.__getattribute__("organization_id"),
                              department_object.__getattribute__("id"))
        if department_exists_flag:
            if len(department_check_error):
                error_message = department_check_error
            else:
                error_message = "Department with this name already exists for this Organization"
                success = False
        else:

            if success:
                if not department_object.__getattribute__("default"):  # Current default status is False
                    if default_status:  # This department is being made default for the org
                        previous_default_department, previous_default_department_error = \
                            get_previous_default_department(conn, department_object.__getattribute__("organization_id"))
                        if previous_default_department:
                            if reset_previous_default_department(conn, previous_default_department):
                                logger.info('Previous default department for org '
                                            + str(department_object.__getattribute__("organization_id"))
                                            + ' has been reset')
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
                                    error_message = "There was an error while assigning new default department to users"
                                    raise Exception(
                                        "Error: There was an error while assigning new default department to users")
                        else:
                            error_message = error_message + previous_default_department_error
                            success = False
                else:  # Current default status is True
                    if not default_status:  # Profile is being made non-default
                        default_departments = get_default_department_id(conn,
                                                                        department_object.__getattribute__(
                                                                            "organization_id"))
                        if len(default_departments) > 0:
                            success = False
                            error_message = error_message + '''Please assign another department as default so that
                                                                this profile will become non-default. '''
        if success:
            update_query = '''Update Departments set Departments.name = %s, Departments.primary_admin = %s,
                    Departments.function = %s, Departments.backup_admin = %s, Departments.default = %s
                    WHERE Departments.id = %s
                    '''
            cur.execute(update_query,
                        (department_name, primary_admin, department_function, backup_admin, int(default_status)
                         , department_object.__getattribute__("id")))
            conn.commit()
    except Exception as ex:
        logger.error("ERROR: Could not update Department " + department_name)
        logger.error(ex)
        success = False
    finally:
        cur.close()
        conn.close()
    if success:
        return {
            'statusCode': 200,
            'body': 'Department updated successfully'
        }
    else:
        return {
            'statusCode': 500,
            'body': error_message
        }
