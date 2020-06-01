
from sqlite3 import Connection
from sqlite3 import OperationalError

import settings


# Executes commands in a SQL file
def execute_sql_from_file(connection, filename):
    fd = open(filename, 'r')
    sql_file = fd.read()
    fd.close()

    commands = sql_file.split(';')

    # Execute every command from the input file
    for command in commands:
        # This will skip and report errors
        # For example, if the tables do not yet exist, this will skip over
        # the DROP TABLE commands
        try:
            connection.execute(command)
        except OperationalError as e:
            print("Command skipped: ", e)

    connection.commit()


def main():
    db = Connection('HumachSurveys.db')

    execute_sql_from_file(connection=db, filename='drop_humach_archive_tables.sql')
    db.commit()
    db.execute('VACUUM;')
    db.commit()

    # make_humach_arhive_tables.sql contains the SQL commands to create the following tables:
    # - samples,
    # - results_standard
    # - results_validation
    execute_sql_from_file(connection=db, filename='make_humach_archive_tables.sql')


if __name__ == '__main__':
    main()


