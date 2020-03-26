import pandas


def rename_in_upper_case(data):
    column_names = data.columns.values
    column_name_map = {name:name.upper() for name in column_names}

    return data.rename(columns=column_name_map)

def upper_values(data):
    column_names = data.columns[data.dtypes=='object']

    data[column_names] = data[column_names].apply(lambda column: column.str.upper()) 

    return data
