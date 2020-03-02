# Kari Palmier    Created 8/26/19
#
#############################################################################
import datetime


def get_month_end(month_str):
    
    if month_str in ['4', '6', '9', '11']:
        end_day = '30'
    elif month_str == '2':
        end_day = '28'
    else:
        end_day = '31'
    
    return end_day


def get_input_date_range():
    start_yr = input('Enter starting year (4 digit format): ')
    start_month = input('Enter starting month (numeric value, Jan = 1): ')
    start_day = input('Enter starting day (default = 1): ')
    if start_day.isnumeric():
        if int(start_day) <= 0 or int(start_day) > 31:
            start_day = '1'
    else:
        start_day = '1'    
    
    end_yr = input('Enter ending year (4 digit format): ')
    end_month = input('Enter ending month (numeric value, Jan = 1): ')
    end_day = input('Enter ending day (default = last day of month): ')
    if end_day.isnumeric():
        if int(end_day) <= 0 or int(start_day) > 31:
            end_day = get_month_end(end_month)
    else:
        end_day = get_month_end(end_month)
    
    start_date = datetime.datetime.strptime('-'.join([start_yr, start_month, start_day]), '%Y-%m-%d')
    end_date = datetime.datetime.strptime('-'.join([end_yr, end_month, end_day]), '%Y-%m-%d')
    
    current_date = datetime.datetime.now()
    
    if end_date > current_date:
        end_date_str = current_date.strftime('%Y-%m-%d')
    else:
        end_date_str = end_yr + '-' + end_month + '-' + end_day
    
    date_range_str = start_yr + '-' + start_month  + '-' + start_day + '_to_' + end_date_str

    return start_date, end_date, date_range_str