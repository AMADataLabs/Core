
GET_LICENSE_PPMA_MISMATCH_DATA = \
    """
    SELECT
        l.entity_id,
        l.state_cd AS license_state,
        l.lic_issue_dt,
        l.lic_exp_dt,
        l.lic_sts,
        ppma.comm_id AS ppma_comm_id,
        ppma.state_cd as ppma_state,
        ppma.usg_begin_dt AS ppma_begin_dt,
        addr.comm_id AS license_addr_comm_id,
        addr.addr_line0,
        addr.addr_line1,
        addr.addr_line2,
        addr.city_cd,
        addr.state_cd AS license_addr_state,
        addr.zip

    FROM
        license_lt l
        INNER JOIN
        (
            SELECT usg.entity_id, usg.comm_id, usg.usg_begin_dt, usg.comm_usage, addr.state_cd
            FROM
                entity_comm_usg_at usg
                INNER JOIN post_addr_at addr
                ON addr.comm_id = usg.comm_id
            WHERE
                usg.comm_usage = 'PP' AND
                usg.end_dt IS NULL
        ) as ppma
        ON ppma.entity_id = l.entity_id
        INNER JOIN
        post_addr_at addr
        ON addr.comm_id = l.comm_id

    WHERE
        l.lic_sts = 'A' AND
        l.lic_issue_dt > ppma.usg_begin_dt AND
        l.state_cd <> ppma.state_cd AND
        ppma.state_cd <> addr.state_cd
    """.strip()
