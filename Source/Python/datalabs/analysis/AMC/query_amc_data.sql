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