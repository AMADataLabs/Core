# Kari Palmier    Created 7/17/19
#
# Required file format:
#
# AIMS username = kpalmier, AIMS password = ****
# EDW username = kpalmier, EDW password = ****
#
#############################################################################

def get_ddb_logins(ddb_login_file):
    
    f = open(ddb_login_file, 'r')
    contents = f.readlines()
    
    ddb_info = {}
    for line in contents:
        tmp_list = line.strip().split(',')
        
        for tmp in tmp_list:
            
            if tmp.find('username') > 0:            
                type_str = 'username'
            else:
                type_str = 'password'
                
            type_ndx = tmp.find(type_str)           
            ddb_name = tmp[0:type_ndx - 1].strip().upper()
            
            entry_ndx = tmp.find('=')
            entry = tmp[entry_ndx + 1:].strip()
            
            if ddb_name in ddb_info.keys():
                ddb_info[ddb_name][type_str] = entry
            else:
                ddb_info[ddb_name] = {}
                ddb_info[ddb_name][type_str] = entry
                
    return ddb_info
            
        




