import pandas as pd
import pyodbc
import os
import settings


def get_newest(path, text):
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files if text in basename]
    return max(paths, key=os.path.getctime)

def get_ppd():
    ppd_loc =  os.environ.get('PPD_FOLDER')
    ppd_file = get_newest(ppd_loc, 'ppd')
    print(ppd_file)
    ppd = pd.read_csv(ppd_file)
    ppd['ME'] = [fix_me(x) for x in ppd.ME]
    return ppd

def fix_zipcode(num):
    num = str(num).strip().replace('.0', '')
    num = ''.join(filter(str.isdigit, num))
    if len(num) > 5:
        num = num[:-4]
    if len(num) == 4:
        num = '0' + num
    elif len(num) == 3:
        num = '00' + num
    elif len(num) == 2:
        num = '000' + num
    return nums
    
def fix_me(me_number):
    num = str(me_number)
    num = num.replace('.0', '')
    if len(num) == 10:
        num = '0' + num
    elif len(num) == 9:
        num = '00' + num
    elif len(num) == 8:
        num = '000' + num
    return num

def fix_phone(num):
    num = str(num).strip().replace('.0', '')
    if num[0] == '1':
        num = num[1:]
    num = ''.join(filter(str.isdigit, num))
    num = num[:10]
    return num

