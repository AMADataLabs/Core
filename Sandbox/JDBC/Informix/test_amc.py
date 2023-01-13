import os
import jaydebeapi

aims = jaydebeapi.connect(
    'com/informix/jdbc/IfxConnection',
    # 'jdbc:informix-sqli://rdbp1627.ama-assn.org:22093/aims_prod',  # :informixserver=prd1srvxnet
    'jdbc:informix-sqli://rdbt1511.ama-assn.org:22035/test_100_pct',
    # 'jdbc:informix-sqli://rdbd1510.ama-assn.org:22040/dev_100_pct',
    [os.getenv('JDBC_USERNAME'), os.getenv('JDBC_PASSWORD')],
    [
        './InformixJdbcDriver/jdbc-4.50.4.1.jar',
        './InformixJdbcDriver/bson-4.2.0.jar'
    ]
)

curs = aims.cursor()
curs.execute("""
    SELECT
        eke.key_type_val as ME,
        ecu.entity_id,
        ecu.comm_id,
        first_nm,
        middle_nm,
        last_nm,
        pa.addr_line0,
        pa.addr_line1,
        pa.addr_line2,
        pa.city_cd,
        pa.zip,
        pa.state_cd,
        ecu.usg_begin_dt,
        ecu.comm_usage

    FROM
        entity_comm_usg_at ecu
        INNER JOIN
        entity_key_et eke
        ON eke.entity_id = ecu.entity_id
        INNER JOIN
        post_addr_at pa
        ON pa.comm_id = ecu.comm_id
        INNER JOIN
        person_name_et pn
        ON pn.entity_id = ecu.entity_id

    WHERE
        ecu.src_cat_code = 'AMC' AND
        ecu.end_dt is null       AND
        eke.key_type ='ME'
    ORDER BY ME SKIP 1 LIMIT 5;
""")
results = curs.fetchall()

print(results)
