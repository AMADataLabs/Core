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


def process_added_users(added_users, conn, group_id):
    success = True
    insert_query = '''INSERT INTO User_Group_Assignment (user_id, group_id) 
                    VALUES ( %s, %s)'''
    for user_id in added_users:
        try:
            cur = conn.cursor()
            cur.execute(insert_query, (user_id, group_id))
            if cur.rowcount < 1:
                raise Exception("Error: Row could not be added")
            else:
                conn.commit()
        except Exception as ex:
            logger.error("ERROR: Could not add User to the Profile")
            logger.error(ex)
            success = False
        finally:
            cur.close()

    return success


def process_deleted_users(deleted_users, conn, group_id):
    success = True
    delete_query = '''Delete from User_Group_Assignment 
                    where user_id = %s and group_id = %s'''

    for user_id in deleted_users:
        try:
            cur = conn.cursor()
            cur.execute(delete_query, (user_id, group_id))
            if cur.rowcount < 1:
                raise Exception("Error: Row could not be deleted")
            else:
                conn.commit()
        except Exception as ex:
            logger.error("ERROR: Could not remove User from the Profile")
            logger.error(ex)
            success = False
        finally:
            cur.close()

    return success


def get_current_users(conn, group_id):
    user_list = []
    get_users_query = '''Select User_Group_Assignment.user_id from User_Group_Assignment 
                    where User_Group_Assignment.group_id = %s'''
    try:
        cur = conn.cursor()
        cur.execute(get_users_query, group_id)
        records = cur.fetchall()
        if len(records) > 0:
            for row in records:
                user_list.append(row[0])
    except Exception as ex:
        logger.error("ERROR: Could not retrieve a list of users of the Profile")
        logger.error(ex)
    finally:
        cur.close()

    return user_list


def get_new_users(current_users, added_users):
    new_users = []
    for added_user in added_users:
        if int(added_user) not in current_users:
            new_users.append(added_user)

    return new_users


def lambda_handler(event, context):
    arn = context.invoked_function_arn
    last_index = arn.rindex(':') + 1
    run_environment = arn[last_index:]
    group_id = event['group_id']
    added_users = event['added']
    deleted_users = event['deleted']
    success = True
    db_host = os.environ.get("DATABASE_HOST")
    user_id = os.environ.get("DATABASE_USERNAME")
    password = os.environ.get("DATABASE_PASSWORD")
    dbname = os.environ.get("DATABASE_NAME")
    row_count = -1
    message = ''
    try:
        conn = pymysql.connect(host=db_host, user=user_id,
                               passwd=password, db=dbname, connect_timeout=50)
        current_users = get_current_users(conn, group_id)
        new_users = get_new_users(current_users, added_users)
        if len(new_users) > 0:
            if process_added_users(new_users, conn, group_id):
                message = message + """Users added to the Profile.
                                    """
            else:
                success = False
                logger.error("ERROR: Could not process added users")
        else:
            if len(added_users) > 0:
                message = message + """No new users added to the Profile.
                                """
        if len(deleted_users) > 0:
            if process_deleted_users(deleted_users, conn, group_id):
                message = message + """Users removed from the Profile.
                                    """
            else:
                success = False
                logger.error("ERROR: Could not process deleted users")
        else:
            if len(message) == 0:
                message = """No users removed from the Profile.
                                """

    except Exception as ex:
        logger.error("ERROR: Could not update Profile Users")
        logger.error(ex)
        success = False
    finally:
        conn.close()
    if success:
        return {
            'statusCode': 200,
            'body': message
        }
    else:
        return {
            'statusCode': 400,
            'body': 'There was an error while updating the Profile Users'
        }
