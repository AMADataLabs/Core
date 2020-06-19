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
        except ValueError as e:
            print("Not a valid SQL command:", e)

    connection.commit()
