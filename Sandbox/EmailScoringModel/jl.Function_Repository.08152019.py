# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 11:01:52 2019

@author: jalee
"""

def data_describe(x):
    print('dimension of dataframe is: ' + str(x.shape)) # dimensions
    print('column names of dataframe are: ' + str(x.columns.values)) # column namess
    print('data types of columns are: ' + str(x.dtypes)) # dtypes
    print('below is the first 5 results: ')
    print(x.head(5)) 

# Import the latest PPD
def PPD_load():
    import os # , sys
    import pandas as pd
    def get_latest_ppd_filename():
        ppd_dir = "U:\\Source Files\\Data Analytics\\Baseline\\data\\"
        files = os.listdir(ppd_dir)
        ppds = []
        # compile a list of the valid PPD files
        for f in files:
            if 'PhysicianProfessionalDataFile_2019' in f:
                ppds.append(f)
        # sort the list in descending order (file name indicates date, desc = newest first)
        ppds.sort(reverse=True)
        # take the first one (newest)
        latest = ppds[0]
        return latest

    ppd_path = "U:\\Source Files\\Data Analytics\\Baseline\\data\\{}".format(get_latest_ppd_filename())
    cols = [
        'ME',
        'RECORD_ID',
        'UPDATE_TYPE',
        'ADDRESS_TYPE',
        'MAILING_NAME',
        'LAST_NAME',
        'FIRST_NAME',
        'MIDDLE_NAME',
        'SUFFIX',
        'MAILING_LINE_1',
        'MAILING_LINE_2',
        'CITY',
        'STATE',
        'ZIP',
        'SECTOR',
        'CARRIER_ROUTE',
        'ADDRESS_UNDELIVERABLE_FLAG',
        'FIPS_COUNTY',
        'FIPS_STATE',
        'PRINTER_CONTROL_CODE',
        'PC_ZIP',
        'PC_SECTOR',
        'DELIVERY_POINT_CODE',
        'CHECK_DIGIT',
        'PRINTER_CONTROL_CODE_2',
        'REGION',
        'DIVISION',
        'GROUP',
        'TRACT',
        'SUFFIX_CENSUS',
        'BLOCK_GROUP',
        'MSA_POPULATION_SIZE',
        'MICRO_METRO_IND',
        'CBSA',
        'CBSA_DIV_IND',
        'MD_DO_CODE',
        'BIRTH_YEAR',
        'BIRTH_CITY',
        'BIRTH_STATE',
        'BIRTH_COUNTRY',
        'GENDER',
        'TELEPHONE_NUMBER',
        'PRESUMED_DEAD_FLAG',
        'FAX_NUMBER',
        'TOP_CD',
        'PE_CD',
        'PRIM_SPEC_CD',
        'SEC_SPEC_CD',
        'MPA_CD',
        'PRA_RECIPIENT',
        'PRA_EXP_DT',
        'GME_CONF_FLG',
        'FROM_DT',
        'TO_DT',
        'YEAR_IN_PROGRAM',
        'POST_GRADUATE_YEAR',
        'GME_SPEC_1',
        'GME_SPEC_2',
        'TRAINING_TYPE',
        'GME_INST_STATE',
        'GME_INST_ID',
        'MEDSCHOOL_STATE',
        'MEDSCHOOL_ID',
        'MEDSCHOOL_GRAD_YEAR',
        'NO_CONTACT_IND',
        'NO_WEB_FLAG',
        'PDRP_FLAG',
        'PDRP_START_DT',
        'POLO_MAILING_LINE_1',
        'POLO_MAILING_LINE_2',
        'POLO_CITY',
        'POLO_STATE',
        'POLO_ZIP',
        'POLO_SECTOR',
        'POLO_CARRIER_ROUTE',
        'MOST_RECENT_FORMER_LAST_NAME',
        'MOST_RECENT_FORMER_MIDDLE_NAME',
        'MOST_RECENT_FORMER_FIRST_NAME',
        'NEXT_MOST_RECENT_FORMER_LAST',
        'NEXT_MOST_RECENT_FORMER_MIDDLE',
        'NEXT_MOST_RECENT_FORMER_FIRST'
    ]
    # read the file and create a DataFrame
    ppd = pd.read_csv(ppd_path, names=cols, sep='|', encoding='IBM437', index_col=False, dtype=object)
    # gauge the size of the DataFrame. This is how much memory the table takes up.
    # bytes_used = ppd.memory_usage(index=True).sum()
    # ppd_size_mb = bytes_used / 1024 / 1024
    return ppd
# change Type of Practice (top) codes into actual values
def TOP_CD(x):
    if x== 12:
        return 'resident'
    elif x==20:
        return 'dpc'
    elif x==30:
        return 'admin'
    elif x==40:
        return 'train'
    elif x==50:
        return 'research'
    elif x==62:
        return 'npc'
    elif x==71:
        return 'retired'
    elif x==72:
        return 'semiretired'
    elif x==74:
        return 'tempout'
    elif x==75:
        return 'inative'
    else :
        return 'unclassified'

def domain(x):
    if '@' in x:
        output = x.split('@')[1]
    else:
        output = x
    return output

def email_name(x):
    output = x.split('@')[0]
    return output 

# refine the variable domain categorical variable on domain names by assigning each ones
# first check if domain contains his or her name
# gmail, hotmail, msn, yahoo, comcast, outlook, cox.net, aol are the most common email servers
# the rest are edu, rr, health, clinic
# anything else are classified as "etc"
def domain_conditions(x,y,z):
    # hard code each domain 
    # if y in x or z in x:
       #  return 'personal' # if the last name is in the domain, then it is a personal domain
    if x == 'gmail.com':
        return 'gmail'
    elif x == 'hotmail.com':
        return 'hotmail'
    elif x == 'msn.com':
        return 'msn'
    elif x == 'yahoo.com':
        return 'yahoo'
    elif x == 'comcast.net':
        return 'comcast'
    elif x == 'outlook.com':
        return 'outlook'
    elif x == 'aol.com':
        return 'aol'
    elif x == 'cox.net':
        return 'cox.net'
    elif 'edu' in x: 
        return 'edu'
    elif '.rr.' in x:
        return 'rr'
    elif 'health' in x: 
        return  'health'
    elif 'clinic' in x:
        return 'clinic'
    else: 
        return 'etc'

# import nickname dictionary
import pandas as pd
nicknames = pd.read_csv("jl.nicknames.08132019.csv")
all_columns = list(nicknames)
nicknames[all_columns] = nicknames[all_columns].astype(str) # change data type to string
# change dataframe into dictionary
nn_dict = {}
for name in nicknames:
    nn_dict[name] = [nick for nick in nicknames[name]]
    if '?' in nn_dict[name]: 
        nn_dict[name] = nn_dict[name][:nn_dict[name].index('?')] # remove '?'

# create a categorical variable for whether it contains full names
# first create a function that takes a first/last name and outputs a possible list of initials
def initial(s):
    i_l = int(0.5*len(s)) # initial length
    if len(s) == 1:
        return [s, s]
    else:
        return [s[:i+1] for i in range(i_l)][::-1]

# next create a function that takes a first/last name and outputs a possible list of full names
# imo, full name should be more conservative than percentage of characters used. But you may disagree and say up to 0.6*len(name) is acceptable as a full name
from math import ceil as ceil
def full(s):
    f_l = ceil(0.5*len(s)) # acceptable full name length
    output = [s[:-i] for i in range(f_l)]
    output[0]=s
    return output
    # if len(s) <= 3: # Lee -> only Lee, not Le
        # return s, s # duplicate s to make it a tuple of length minimum 2; otherwise, later code will read each string character instead of each whole string
    # elif len(s) ==4: 
        # return s, s[:-1]
    # elif len(s) >= 5:
        # return s, s[:-1],s[:-2]

# Takes a list y and remove any element that matches first in x from x
def remover(x,y): # x = email name , y = list of initials or full name
    for i in y: # loop from the last element which should be the longest character
        if i in x:
            return x.replace(i,'')
    return x

# returns boolean whether email contains nickname
def nickname_match(email,fname):
    # email name x, first name y, and  dictionary of nicknames z
    match = nn_dict.get(fname)
    if match == None:
        return False
    else:
        return any([element in email for element in match])
    # check if any of the nicknames are in the email name 
    #return any([element in email for element in match]),

# if s is none, then output an empty list
def NoneList(s):
    if s is None:
        return []
    return s
    
# finally create a function that takes email name, first name, and last name, and outputs one of (Ff_Fl, If_Fl, etc..)
def email_name_conditions(x,y,z):
    # x = email name
    # y = first name, z= last name
    x = ''.join(i for i in x if not i.isdigit()) # remove numbers
    x=x.replace('-','').replace('_','').replace('.','') # remove punctuations
    y=str(y)
    z=str(z)
    y=y.replace(" ","").replace('-','') # remove spaces and dashes
    z=z.replace(" ","").replace('-','')
    x=x.lower() # lowercase
    y=y.lower()
    z=z.lower()
    md_title = ['md','doctor','dr','doc','ds','vet'] # doctor title
    
    # check whether it contains names 
    if (any(substring in x for substring in full(y)) or \
        nickname_match(x,y)) and any(substring in x for substring in full(z)):
            return 'Ff_Fl' # full first name and full last name in email 
    elif any(substring in x for substring in full(z)):
        temp = remover(x, full(z)) # remove last name 
        temp = remover(temp, md_title) # remove medical title
        if any(substring == temp for substring in initial(y)) or \
        (len(temp) == 2 and \
         initial(y)[-1]==temp[0]): # exact match for initials
            return 'If_Fl' # initial first name and full last name in email
        elif len(temp) == 0:
            return 'Only_L' # contains only last name
        else:
            return 'Dif_Person'
    elif any(substring in x for substring in full(y)) or nickname_match(x,y):
        temp = remover(x,full(y)+NoneList(nn_dict.get(y))) # remove first name for whichever one that matched
        temp = remover(temp, md_title)
        if any(substring == temp for substring in initial(z)) or \
        (len(temp) == 2 and initial(z)[-1]==temp[1]):
            return 'Ff_Il' # full first name and initial last name in email
        elif len(temp) == 0:
            return 'Only_F' # contains only first_name
        else:
            return 'Dif_Person'
    elif len(x)<=3: # strip of number in email name and check the length is less than or equal to 3
        if any(substring in x for substring in initial(y)): 
            temp = remover(x, initial(y)) # remove first name initial
            if any(substring in x for substring in initial(z)):
                return 'If_Il' # initial first name and initial last name in email
        if any(substring in x for substring in initial(z)):
            temp = remover(x, initial(z)) # remove last name initial
            if any(substring in x for substring in initial(y)): 
                return 'If_Il'
    else:
        return 'no_name'
    # all the categories: 'Ff_Fl', 'If_Fl', 'Ff_Il', 'Only_L', 'Only_F', 'Dif_Person', 'no_name'

# creates a boolean variable for whether email name contains a number
import re
def hasNum(s):
    return bool(re.search(r'\d',s))

# remove numbers and see if the last two characters are md
# creates a boolean variable for whether email name contains 'md'
def hasMD(s):
    s = ''.join(i for i in s if not i.isdigit())
    s = s.lower()
    return s[-2:]=='md'

# the first two characters are dr
# creates a boolean variable for whether email name contains 'dr'
def hasDR(s):
    s = ''.join(i for i in s if not i.isdigit())
    s = s.lower()
    return s[:2]=='dr'

# creates a boolean variable for whether email name contains 'doc'
def hasDOC(s):
    return bool(re.search('doc',s))
