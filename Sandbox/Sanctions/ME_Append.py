import pandas as pd
import pyodbc

# needs to be refactored to the new authentication/connection method from Peter
username = ''
password = ''
AIMS_conn = pyodbc.connect('DSN=aims_prod; UID={}; PWD={}'.format(username, password))
AIMS_conn.execute('SET ISOLATION TO DIRTY READ;')


def get_me_nbr(first, last, state, lic_nbr, con):
    # initial search is just on first + last because I was getting some weird errors / unexpected behavior when
    # using state_cd to compare to state in the SQL query. Final matching on state and license number are done
    # once the initial results are in a DataFrame.
    sql_template = \
        """
        SELECT 
            ek.key_type_val,
            nm.first_nm,
            nm.last_nm,
            lic.lic_nbr,
            lic.state_cd
    
        FROM
            person_name_et nm
    
            INNER JOIN
            entity_key_et ek
            ON nm.entity_id = ek.entity_id
    
            INNER JOIN
            license_lt lic
            ON lic.entity_id = ek.entity_id
    
        WHERE
            ek.key_type          = "ME"    AND
            UPPER(nm.first_nm)   = "{}"    AND
            UPPER(nm.last_nm)    = "{}"
        ;
        """

    sql = sql_template.format(first.upper(), last.upper())

    data = pd.read_sql(con=con, sql=sql)

    # sometimes the license number in our databases has a prefix, "MD" or "DO" to designate license type.
    # to be flexible with unknown prefixes/suffixes, I just look to see if our license number contains the target.
    data = data[(data['state_cd'] == state) & (data['lic_nbr'].apply(lambda x: str(lic_nbr) in x))].drop_duplicates()

    # we should only have one result at this point--duplicates on name + state + license should be impossible
    if len(data) == 1:
        return data['key_type_val'].apply(str.strip).values[0]

    # if there were no results, it's possible that first and last name in the metadata file were swapped. New search.
    else:
        sql = sql_template.format(last, first)
        data = pd.read_sql(con=con, sql=sql)

        data = data[(data['state_cd'] == state) & (data['lic_nbr'].apply(lambda x: str(lic_nbr) in x))].drop_duplicates()

        if len(data) == 1:
            return data['key_type_val'].apply(str.strip).values[0]

        # no luck.
        else:
            return None


"""
# Examples
get_me_nbr(first='KATHARINE',
           last='ALTIERI',
           state='AZ',
           lic_nbr=50790,
           con=AIMS_conn) == '00518110934'
           
# swap first and last name
get_me_nbr(first='ALTIERI',
           last='KATHARINE',
           state='AZ',
           lic_nbr=50790,
           con=AIMS_conn) == '00518110934'
"""
