""" SQL Query """
SQL_TEMPLATE = \
    """
    SELECT
        ek.key_type_val,
        nm.first_nm,
        nm.last_nm,
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
        UPPER(nm.last_nm)    ="{}";
    """.strip()
