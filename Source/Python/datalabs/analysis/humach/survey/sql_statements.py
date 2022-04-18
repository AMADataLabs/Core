""" Docfile string go brrrrrrrr """
MAKE_TABLE_RESULTS = \
    """
    CREATE TABLE IF NOT EXISTS humach_result(
        sample_id INTEGER NOT NULL,
        row_id INTEGER NOT NULL,
        physician_me_number VARCHAR,
        physician_first_name VARCHAR,
        physician_middle_name VARCHAR,
        physician_last_name VARCHAR,
        suffix VARCHAR,
        degree VARCHAR,
        office_address_line_1 VARCHAR,
        office_address_line_2 VARCHAR,
        office_address_city VARCHAR,
        office_address_state VARCHAR,
        office_address_zip VARCHAR,
        office_address_verified_updated VARCHAR,
        office_telephone VARCHAR,
        office_phone_verified_updated VARCHAR,
        office_fax VARCHAR,
        office_fax_verified_updated VARCHAR,
        specialty VARCHAR,
        specialty_updated VARCHAR,
        present_employment_code VARCHAR,
        present_employment_updated VARCHAR,
        comments VARCHAR,
        source VARCHAR,
        source_date DATE
    );
    """.strip()

MAKE_TABLE_SAMPLES = \
    """
    CREATE TABLE IF NOT EXISTS humach_sample(
        sample_id INTEGER NOT NULL,
        row_id INTEGER NOT NULL,
        survey_month INTEGER NOT NULL,
        survey_year INTEGER NOT NULL,
        survey_type VARCHAR NOT NULL,
        sample_source VARCHAR,
        me VARCHAR,
        entity_id VARCHAR,
        first_name VARCHAR,
        middle_name VARCHAR,
        last_name VARCHAR,
        suffix VARCHAR,
        polo_comm_id VARCHAR,
        polo_mailing_line_1 VARCHAR,
        polo_mailing_line_2 VARCHAR,
        polo_city VARCHAR,
        polo_state VARCHAR,
        polo_zip VARCHAR,
        phone_comm_id VARCHAR,
        telephone_number VARCHAR,
        prim_spec_cd VARCHAR,
        description VARCHAR,
        pe_cd VARCHAR,
        fax_number VARCHAR
    );
    """.strip()

MAKE_TABLE_REFERENCE = \
    """
    CREATE TABLE IF NOT EXISTS sample_reference(
        humach_sample_id INTEGER NOT NULL,
        other_sample_id INTEGER NOT NULL,
        other_sample_source VARCHAR NOT NULL
    );
    """

MAKE_TABLE_VALIDATION_RESULT = \
    """
    CREATE TABLE IF NOT EXISTS validation_result(
        sample_id INTEGER NOT NULL,
        row_id INTEGER NOT NULL,
        study_cd VARCHAR,
        me_no VARCHAR,
        fname VARCHAR,
        mname VARCHAR,
        lname VARCHAR,
        suffix VARCHAR,
        degree VARCHAR,
        lable_name VARCHAR,
        office_phone VARCHAR,
        polo_addr_line_0 VARCHAR,
        polo_addr_line_1 VARCHAR,
        polo_addr_line_2 VARCHAR,
        polo_city VARCHAR,
        polo_state VARCHAR,
        polo_zip VARCHAR,
        polo_zipext VARCHAR,
        original_phone VARCHAR,
        correct_phone VARCHAR,
        reason_phone_incorrect VARCHAR,
        reason_phone_other VARCHAR,
        captured_number VARCHAR,
        correct_address VARCHAR,
        reason_addr_incorrect VARCHAR,
        reason_addr_other VARCHAR,
        no_longer_at_addr_comment VARCHAR,
        captured_add0 VARCHAR,
        captured_add1 VARCHAR,
        captured_add2 VARCHAR,
        captured_city VARCHAR,
        captured_state VARCHAR,
        captured_zip VARCHAR,
        captured_zipext VARCHAR,
        lastcall VARCHAR,
        adcid VARCHAR,
        secondattempt VARCHAR,
        result_of_call VARCHAR
    );
    """

DROP_TABLE_SAMPLES = "DROP TABLE IF EXISTS humach_sample"

DROP_TABLE_RESULTS = "DROP TABLE IF EXISTS humach_result"

DROP_TABLE_REFERENCE = "DROP TABLE IF EXISTS sample_reference"

DROP_TABLE_VALIDATION_RESULT = "DROP TABLE IF EXISTS validation_result"
