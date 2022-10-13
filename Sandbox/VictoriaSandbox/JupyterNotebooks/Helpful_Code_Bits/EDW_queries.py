def get_insurance_addresses(FROM_DT = '2019-01-01 00:00:00.000000'):
    s = "DSN=PRDDW; UID={}; PWD={}".format(username, password)
    AMAEDW = pyodbc.connect(s)

    sql_query2 = \
    f""" 
    SELECT DISTINCT
    A.PARTY_ID, 
    K.KEY_VAL AS ME, 
    A.POST_CD_ID,
    A.FROM_DT,
    C.PURPOSE_TYPE_DESC AS ADDR_TYPE, 
    P.ADDR_1, 
    P.ADDR_2, 
    P.ADDR_3, 
    P.CITY, 
    S.SRC_STATE_CD AS STATE_CD, 
    P.POST_CD AS ZIP
    FROM 
    AMAEDW.PARTY_KEY K, AMAEDW.PARTY_ADDR A, AMAEDW.CONT_PURPOSE_TYPE C, AMAEDW.POST_CD P, AMAEDW.STATE S 
    WHERE  
    A.THRU_DT IS NULL
    AND
    K.PARTY_ID = A.PARTY_ID 
    AND 
    K.KEY_TYPE_ID = 18 
    AND 
    K.ACTIVE_IND = 'Y'
    AND
    C.PURPOSE_TYPE_ID IN (1)
    AND
    A.POST_CD_ID = P.POST_CD_ID 
    AND
    P.STATE_ID = S.STATE_ID
    AND
    P.SRC_SYS = 'MASTERFILE'
    AND
    A.FROM_DT > {FROM_DT};
    """
    insurance = pd.read_sql(con=AMAEDW, sql=sql_query)

    insurance = insurance.sort_values(by='FROM_DT')

    return(insurance)