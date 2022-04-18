""" Serial SQL statement execution helper function. """
def execute_sql_from_file(connection, filename):
    sql_file = None

    with open(filename, 'r') as file:
        sql_file = file.read()

    commands = sql_file.split(';')

    # Execute every command from the input file
    for command in commands:
        # This will skip and report errors
        # For example, if the tables do not yet exist, this will skip over
        # the DROP TABLE commands
        try:
            connection.execute(command)
        except ValueError as exception:
            print("Not a valid SQL command:", exception)

    connection.commit()
