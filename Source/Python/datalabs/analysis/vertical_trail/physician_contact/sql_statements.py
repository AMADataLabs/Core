MAKE_TABLE_SAMPLES = \
    """
    CREATE TABLE IF NOT EXISTS vertical_trail_samples(
        sample_id INTEGER NOT NULL,
        row_id INTEGER NOT NULL,
        sample_date DATE NOT NULL,
        me VARCHAR NOT NULL,
        last_name VARCHAR,
        first_name VARCHAR,
        middle_name VARCHAR,
        medschool_grad_year VARCHAR,
        medschool_name VARCHAR,
        degree_type VARCHAR,
        specialty VARCHAR,
        polo_city VARCHAR,
        polo_state VARCHAR,
        polo_zip VARCHAR,
        lic_state VARCHAR,
        lic_nbr VARCHAR,
        oldphone1 VARCHAR,
        oldphone2 VARCHAR,
        oldphone3 VARCHAR,
        oldphone4 VARCHAR,
        oldphone5 VARCHAR,
        oldphone6 VARCHAR,
        oldphone7 VARCHAR,
        oldphone8 VARCHAR,
        oldphone9 VARCHAR,
        oldphone10, VARCHAR,
        oldphone11 VARCHAR,
        oldphone12 VARCHAR,
        oldphone13 VARCHAR
    );
    """.strip()

MAKE_TABLE_RESULTS = \
    """
    CREATE TABLE IF NOT EXISTS vertical_trail_results(
        sample_id INTEGER NOT NULL,
        row_id INTEGER NOT NULL,
        phone_number VARCHAR,
        fax_number VARCHAR,
        email VARCHAR,
        notes VARCHAR
    );
    """.strip()

DROP_TABLE_SAMPLES = "DROP TABLE IF EXISTS vertical_trail_samples"

DROP_TABLE_RESULTS = "DROP TABLE IF EXISTS vertical_trail_results"
