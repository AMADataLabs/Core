from dataclasses import dataclass
import pandas as pd
import numpy as np 
from datetime import datetime

@dataclass
class MeasurementParameters:
    name: str
    data_type: str
    location: str
    element: str
    measure: str
    is_not: bool
    condition_indicator: bool
    condition_column: str
    condition_value: list
    method: str
    value: list
    condition_is_not: bool

def get_methods(methods, measure):
    measure_methods = {}
    for row in methods[methods.MEASURE==measure].itertuples():
        if type(row.CONDITION_VALUE) == str:
            condition_values = row.CONDITION_VALUE.split(' ')
        else:
            condition_values = [row.CONDITION_VALUE]
        if type(row.VALUE) == str:
            values = row.VALUE.split(' ')
        else:
            values = [row.VALUE]
        measure_methods[row.COLUMN_NAME] = MeasurementParameters(row.DATA_ELEMENT,
                                                                row.DATA_TYPE,
                                                                row.DATABASE_LOCATION,
                                                                row.COLUMN_NAME,
                                                                row.MEASURE,
                                                                row.NOT,
                                                                row.CONDITION_INDICATOR,
                                                                row.CONDITION_COLUMN,
                                                                condition_values,
                                                                row.METHOD,
                                                                values,
                                                                row.CONDITION_IS_NOT)
    return measure_methods
        
def fill(raw_value, measurement_parameters):
    if type(raw_value) == float:
        if np.isnan(raw_value):
            measure = False
        else:
            bad_list = measurement_parameters.value.extend(['', '-1', ' '])
            measure = str(raw_value).replace('.0') not in measurement_parameters.value
    else:
        measure = str(raw_value).replace('.0') not in measurement_parameters.value
    return measure

#in progress
def conditional(row_dict, measurement_parameters):
    if measurement_parameters.condition_indicator:
        if measurement_parameters.condition_is_not:
            eligible = row_dict[measurement_parameters.condition_column] not in values
        else:
            eligible = row_dict[measurement_parameters.condition_column] in values
    else:
        eligible = True
    return eligible

def length(raw_value, measurement_parameters):
    valid =  len(raw_value) == len(measurement_parameters.value())
    return valid

def valid_list(raw_value, measurement_parameters):
    if measurement_parameters.is_not:
        valid = raw_value not in measurement_parameters.value
    else:
        valid = raw_value in measurement_parameters.value
    return valid

def link(raw_value, measurement_parameters, folder):
    filename = f'{folder}{measurement_parameters.value}'
    with open(filename) as f:
        valid_list = f.read().splitlines()
    valid = raw_value in valid_list
    return valid

def invalid_characters(raw_value, measurement_parameters):
    valid =  True
    for value in measurement_parameters.value:
        if value in raw_value:
            valid = False
            break
    return valid

def datatype(raw_value, measurement_parameters):
    if measurement_parameters.value == 'datetime':
        valid = type(raw_value) == datetime
    return valid

def part_equal_value(raw_value, measurement_parameters):
    if measurement_parameters.is_not:
        for value in measurement_parameters.value:
            if value in raw_value:
                valid = False
                break
    else:
        for value in measurement_parameters.value:
            if value in raw_value:
                valid = True
                break
    return valid

def equal_columns_local(row_dict, measurement_parameters):
    composite_value = ''
    for column in measurement_parameters.value:
        composite_value = composite_value + ' ' + row_dict[column]
    valid = row_dict[measurement_parameters.column_name] == composite_value
    return valid

def newer_date(raw_value, measurement_parameters):
    raw_value = datetime.strp_time(raw_value, '%m/%d/%Y')
    date_constraint = datetime.strp_time(measurement_parameters.value, '%m/%d/%Y')
    valid = raw_value > date_constraint
    return valid

def older_date_column(row_dict, measurement_parameters):
    raw_value = datetime.strp_time(measurement_parameters.column_name, '%m/%d/%Y')
    date_constraint = datetime.strp_time(row_dict[measurement_parameters.value], '%m/%d/%Y')
    valid = raw_value < date_constraint
    return valid

def which_method(method_parameters, raw_value):
    method = method_parameters.method
    if method == 'fill':
        return fill(raw_value, method_parameters)
    elif method == 'length':
        return length(raw_value, method_parameters)
    elif method == 'invalid_characters':
        return invalid_characters(raw_value, method_parameters)
    elif method == 'link':
        return link(raw_value, method_parameters)
    elif method == 'part_equal_value':
        return part_equal_value(raw_value, method_parameters)
    elif method == 'datatype':
        return datatype(raw_value, method_parameters)
    elif method == 'newer_date':
        return newer_date(raw_value, method_parameters)

def measure_row(row_dict, methods_df, measure):
    methods = get_methods(methods_df, measure)
    dict_list = []
    for key in row_dict.keys():
        if key in methods.keys():
            if conditional(row_dict, methods[key]):
                value = which_method(methods[key], row_dict[key])
            else:
                continue
            new_dict = {
                'ME_KEY': row_dict['ME'],
                'ELEMENT': key,
                'MEASURE': methods[key].measure,
                'VALUE': value,
                'RAW_VALUE': row_dict[key]
            }
            dict_list.append(new_dict)
        else:
            continue
    return dict_list