import pandas


def rename_in_upper_case(data):   
    column_names = data.columns.values
    column_name_map = {name:name.upper() for name in column_names}
    
    return data.rename(columns=column_name_map)
