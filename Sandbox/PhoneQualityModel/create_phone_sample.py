

def get_db_login(database_name):

    # more to add as necessary
    db_env_vars = {
        'aims': 'auth_aims',
        'edw': 'auth_edw'
    }
    database_name = database_name.lower()
    var = db_env_vars[database_name]
    env_var = os.getenv(var)

    username, password = (env_var.split())
    return username, password
