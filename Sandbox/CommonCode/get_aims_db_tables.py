# Kari Palmier    Created 8/8/19
#
#############################################################################
import os
import sys

import pandas as pd
import pyodbc

import datalabs.curate.dataframe as df



def format_list_for_sql(lst):
    sql_str = '(' + str(lst[0])
    remain_lst = lst[1:]
    for i in remain_lst:
        sql_str += ',' + str(i)
    sql_str += ')'
        
    return sql_str


def get_entity_me_key(AIMS_conn):

    entity_key_query = \
        """
        SELECT key_type_val as me, entity_id
        FROM entity_key_et 
        WHERE key_type = 'ME'
        """    
        
    entity_key_df = pd.read_sql(entity_key_query, AIMS_conn)
    
    entity_key_df = df.strip(entity_key_df)
    
    return entity_key_df


# get entity_comm_at, phone_at, and me info for latest begin date of each me/entity_id
# remove any entries with an entity_comm_at end_dt present 
# (means number has been end dated and should not be used)
def get_ent_comm_phones(AIMS_conn):
    
    entity_comm_query = \
        """
        SELECT e.*, p.area_cd||p.exchange||p.phone_nbr as aims_phone
        FROM entity_comm_at e join phone_at p on e.comm_id = p.comm_id
        WHERE comm_cat = 'P'
        """    
    entity_comm_df = pd.read_sql(entity_comm_query, AIMS_conn)
    entity_comm_df['aims_phone'] = entity_comm_df['aims_phone'].apply(lambda x: x.replace(' ',''))
        
    
    entity_key_df = get_entity_me_key(AIMS_conn)
    
    entity_comm_me_df = entity_comm_df.merge(entity_key_df, how = 'inner', on = 'entity_id')
    
    entity_comm_me_df = df.strip(entity_comm_me_df)

    return entity_comm_me_df


def get_comm_usg_preferred_phones(AIMS_conn):
    
    entity_comm_usg_query = \
        """
        SELECT e.*, p.area_cd||p.exchange||p.phone_nbr as aims_phone
        FROM entity_comm_usg_at e join phone_at p on e.comm_id = p.comm_id
        WHERE comm_usage = 'PV'
        """    
    entity_comm_usg_df = pd.read_sql(entity_comm_usg_query, AIMS_conn)
    entity_comm_usg_df['aims_phone'] = entity_comm_usg_df['aims_phone'].apply(lambda x: x.replace(' ',''))
        
    
    entity_key_df = get_entity_me_key(AIMS_conn)
    
    ent_comm_usg_me_df = entity_comm_usg_df.merge(entity_key_df, how = 'inner', on = 'entity_id')

    ent_comm_usg_me_df = df.strip(ent_comm_usg_me_df)

    return ent_comm_usg_me_df


def get_comm_usg_all_phones(AIMS_conn):
    
    entity_comm_usg_query = \
        """
        SELECT e.*, p.area_cd||p.exchange||p.phone_nbr as aims_phone
        FROM entity_comm_usg_at e join phone_at p on e.comm_id = p.comm_id
        WHERE comm_cat = 'P'
        """    
    entity_comm_usg_df = pd.read_sql(entity_comm_usg_query, AIMS_conn, coerce_float = False)
    entity_comm_usg_df['aims_phone'] = entity_comm_usg_df['aims_phone'].apply(lambda x: x.replace(' ',''))
        
    
    entity_key_df = get_entity_me_key(AIMS_conn)
    
    ent_comm_usg_me_df = entity_comm_usg_df.merge(entity_key_df, how = 'inner', on = 'entity_id')

    ent_comm_usg_me_df = df.strip(ent_comm_usg_me_df)

    return ent_comm_usg_me_df


def get_uniq_active_ent_info(entity_df, phone_fax_var, begin_dt_var, end_dt_var):
        
    entity_no_end_df = entity_df[entity_df[end_dt_var].isna()]
    entity_me_uniq_df = entity_no_end_df.sort_values([begin_dt_var], ascending = False).groupby(['me', 
                                                    phone_fax_var]).first().reset_index()
    
    return entity_me_uniq_df


def get_active_licenses(AIMS_conn):
       
    license_query = \
        """
        SELECT *
        FROM license_lt
        WHERE lic_sts = 'A'
        """    
    license_df = pd.read_sql(license_query, AIMS_conn)
    
    license_df = df.strip(license_df)

    return license_df
   
    
def get_no_contacts(AIMS_conn):
    
    no_contact_query = \
        """
        SELECT *
        FROM entity_cat_ct
        WHERE (end_dt is null and category_code = 'NO-CONTACT') or 
        (end_dt is null and category_code = 'NO-EMAIL') or 
        	     (end_dt is null and category_code = 'NO-RELEASE')
        """    
    no_contact_df = pd.read_sql(no_contact_query, AIMS_conn)
    
    no_contact_df = df.strip(no_contact_df)

    return no_contact_df
   
    
def get_pe_description(AIMS_conn):
    
    pe_desc_query = \
       """
       SELECT present_emp_cd, description
       FROM present_emp_pr
       """    
    pe_desc_df = pd.read_sql(pe_desc_query, AIMS_conn)
    
    pe_desc_df = df.strip(pe_desc_df)

    return pe_desc_df
   
 
def get_spec_description(AIMS_conn):
    
    spec_desc_query = \
       """
       SELECT spec_cd, description
       FROM spec_pr
       """    
    spec_desc_df = pd.read_sql(spec_desc_query, AIMS_conn)
    
    spec_desc_df = df.strip(spec_desc_df)

    return spec_desc_df

    
def get_all_ent_comm_addrs(AIMS_conn):
    
    entity_comm_query = \
        """
        SELECT e.*, p.addr_line2, p.addr_line1, p.city_cd, p.state_cd, p.zip
        FROM entity_comm_at e join post_addr_at p on e.comm_id = p.comm_id
        WHERE comm_cat = 'A'
        """    
    entity_comm_df = pd.read_sql(entity_comm_query, AIMS_conn)       
    
    entity_key_df = get_entity_me_key(AIMS_conn)
    
    entity_comm_me_df = entity_comm_df.merge(entity_key_df, how = 'inner', on = 'entity_id')
    
    entity_comm_me_df = df.strip(entity_comm_me_df)

    return entity_comm_me_df


def get_all_comm_usg_addrs(AIMS_conn):
    
    entity_comm_usg_query = \
        """
        SELECT e.*, p.addr_line2, p.addr_line1, p.city_cd, p.state_cd, p.zip
        FROM entity_comm_usg_at e join post_addr_at p on e.comm_id = p.comm_id
        WHERE comm_cat = 'A'
        """    
    entity_comm_usg_df = pd.read_sql(entity_comm_usg_query, AIMS_conn)
    
    entity_key_df = get_entity_me_key(AIMS_conn)
    
    ent_comm_usg_me_df = entity_comm_usg_df.merge(entity_key_df, how = 'inner', on = 'entity_id')

    ent_comm_usg_me_df = df.strip(ent_comm_usg_me_df)

    col_names = ent_comm_usg_me_df.columns.values
    new_col_dict = {}
    for name in col_names:
        if name.find('usg') >= 0:
            new_col_dict[name] = name
        else:
            new_name = 'usg_' + name
            new_col_dict[name] = new_name
            
    ent_comm_usg_me_df = ent_comm_usg_me_df.rename(columns = new_col_dict)
    
    return ent_comm_usg_me_df


def get_all_post_addr_at(AIMS_conn):
    
    post_addr_query = \
        """
        SELECT p.*
        FROM post_addr_at p
        """    
    post_addr_df = pd.read_sql(post_addr_query, AIMS_conn)       
    
    post_addr_df = df.strip(post_addr_df)
    
    return post_addr_df


def get_me_ent_comm_addrs(AIMS_conn, me_lst):
    
    me_sql_lst = format_list_for_sql(list(me_lst))
    
    entity_comm_query = \
        """
        SELECT e.*, k.key_type_val as me, p.addr_line2, p.addr_line1, p.city_cd, p.state_cd, p.zip
        FROM entity_comm_at e 
        INNER JOIN post_addr_at p ON e.comm_id = p.comm_id
        INNER JOIN entity_key_et k ON e.entity_id = k.entity_id
        WHERE comm_cat = 'A'
        AND k.key_type_val IN {}
        """.format(me_sql_lst)
        
    entity_comm_df = pd.read_sql(entity_comm_query, AIMS_conn)       
    
    entity_key_df = get_entity_me_key(AIMS_conn)
    
    entity_comm_me_df = entity_comm_df.merge(entity_key_df, how = 'inner', on = 'entity_id')
    
    entity_comm_me_df = df.strip(entity_comm_me_df)

    return entity_comm_me_df



    
    
    
    
    
    
    

