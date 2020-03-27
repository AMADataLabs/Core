""" Utility functions for curating data in Pandas DataFrames. """


def rename_in_upper_case(data):
    """ Like DataFrame.rename() but new names are the old names converted to upper case. """
    column_names = data.columns.values
    column_name_map = {name:name.upper() for name in column_names}

    return data.rename(columns=column_name_map)


def upper(data):
    """ Convert all string values in the DataFrame to upper case. """
    column_names = data.columns[data.dtypes == 'object']

    data[column_names] = data[column_names].apply(lambda column: column.str.upper())

    return data


def strip(data):
    """ Apply string.strip() to all string values in the DataFrame. """
    column_names = data.columns[data.dtypes == 'object']

    data[column_names] = data[column_names].apply(lambda column: column.str.strip())

    return data
