"Define AMA PROFILE COLUMNS"
AMA_PROFILE_COLUMNS = {
    "ENTITY_ID": "tempProfileId",
    "FIRST_NAME": "firstName",
    "LAST_NAME": "lastName",
    "DEGREE_CD": "degreeCode",
    "POLO_CITY_NM": "city",
    "POLO_STATE_ID": "state",
    "POLO_ZIP": "zipcode",
    "ME_NBR": "meNumber"
}


NPI_COLUMNS = {
    "NPI_DATA_ID": "npiDataId",
    "ENTITY_ID": "entityId",
    "NPI_CD": "npiCd",
    "ENUMERATION_DT": "enumerationDate",
    "DEACTIVATION_DT": "deactivationDate",
    "REACTIVATION_DT": "reactivationDate",
    "REP_NPI_CD": "repNpiCode",
    "RPTD_DT": "rptdDate",
    # "INSERT_DTM": "insertDtm",
    # "INSERT_USER_ID": "insertUserId",
    "END_DT": "endDate",
    "FIRST_NAME": "firstName",
    "MIDDLE_NAME": "middleName",
    "LAST_NAME": "lastName",
}

DEMOG_DATA_COLUMNS = [
    "ENTITY_ID",
    "PRIMARY_SPECIALTY",
    "SECONDARY_SPECIALTY",
    "NAME_PREFIX",
    "FIRST_NAME",
    "MIDDLE_NAME",
    "LAST_NAME",
    "NAME_SUFFIX",
    "BIRTH_DT",
    "EMAIL_ADDRESS",
    "DEATH_DT",
    "STUDENT_IND",
    "CUT_IND",
    "STATUS_DESC",
    "PRA_EXPR_DT",
    "DEGREE_CD",
    "NAT_BRD_YEAR",
    "MAILING_ADDRESS_LINE_1",
    "MAILING_ADDRESS_LINE_2",
    "MAILING_ADDRESS_LINE_3",
    "MAILING_CITY_NM",
    "MAILING_STATE_ID",
    "MAILING_ZIP",
    "ADDR_UNDELIVERABLE_IND",
    "POLO_ADDRESS_LINE_1",
    "POLO_ADDRESS_LINE_2",
    "POLO_ADDRESS_LINE_3",
    "POLO_CITY_NM",
    "POLO_STATE_ID",
    "POLO_ZIP",
    "PHONE_PREFIX",
    "PHONE_AREA_CD",
    "PHONE_EXCHANGE",
    "PHONE_NUMBER",
    "PHONE_EXTENSION",
    "MPA_DESC",
    "ECFMG_NBR",
    "ME_NBR",
    "LABEL_NAME",
    "PRINT_PHONE_NUMBER"
]

DEA_COLUMNS = {
    "DEA_NBR": "deaNumber",
    "DEA_SCHEDULE": "schedule",
    "DEA_AS_OF_DT": "lastReportedDate",
    "DEA_EXPR_DT": "expirationDate",
    "BUSINESS_ACTIVITY": "businessActivity",
    "DEA_STATUS_DESC": "activityStatus",
    "PAYMENT_IND": "paymentInd"
}

ADDRESS_COLUMNS = {
    "ADDRESS_LINE_1": "line1",
    "ADDRESS_LINE_2": "line2",
    "ADDRESS_LINE_3": "line3",
    "CITY_NM": "city",
    "STATE_ID": "state",
    "ZIP": "zip"
}

DEMOGRAPHICS_COLUMNS = {
    "NAME_PREFIX": "prefix",
    "FIRST_NAME": "firstName",
    "MIDDLE_NAME": "middleName",
    "LAST_NAME": "lastName",
    "NAME_SUFFIX": "suffix",
    "BIRTH_DT": "birthDate",
    "EMAIL_ADDRESS": "emailAddress",
    "DEATH_DT": "deathDate",
    "STUDENT_IND": "studentIndicator",
    "CUT_IND": "cutIndicator",
    "STATUS_DESC": "amaMembershipStatus",
    "PRA_EXPR_DT": "praExpirationDate",
    "DEGREE_CD": "degreeCode",
    "NAT_BRD_YEAR": "nbmeYear",
    "LABEL_NAME": "printName"
}

MAILING_ADDRESS_COLUMNS = {
    "MAILING_ADDRESS_LINE_1": "line1",
    "MAILING_ADDRESS_LINE_2": "line2",
    "MAILING_ADDRESS_LINE_3": "line3",
    "MAILING_CITY_NM": "city",
    "MAILING_STATE_ID": "state",
    "MAILING_ZIP": "zip",
    "ADDR_UNDELIVERABLE_IND": "addressUndeliverable"
}

OFFICE_ADDRESS_COLUMNS = {
    "POLO_ADDRESS_LINE_1": "line1",
    "POLO_ADDRESS_LINE_2": "line2",
    "POLO_ADDRESS_LINE_3": "line3",
    "POLO_CITY_NM": "city",
    "POLO_STATE_ID": "state",
    "POLO_ZIP": "zip",
}

PHONE_COLUMNS = {
    "PHONE_PREFIX": "prefix",
    "PHONE_AREA_CD": "areaCode",
    "PHONE_EXCHANGE": "exchange",
    "PHONE_NUMBER": "number",
    "PHONE_EXTENSION": "extension",
    "PRINT_PHONE_NUMBER": "phoneNumber"
}

PRACTICE_SPECIALTIES_COLUMNS = {
    "PRIMARY_SPECIALTY": "primarySpecialty",
    "SECONDARY_SPECIALTY": "secondarySpecialty",
}

NPI_COLUMNS = {
    "NPI_CD": "npiCode",
    "ENUMERATION_DT": "enumerationDate",
    "DEACTIVATION_DT": "deactivationDate",
    "REACTIVATION_DT": "reactivationDate",
    "REP_NPI_CD": "repNPICode",
    "RPTD_DT": "lastReportedDate",
}

MEDICAL_SCHOOL_COLUMNS = {
    "GRAD_STATUS": "degreeAwarded",
    "SCHOOL_NAME": "schoolName",
    "GRAD_DT": "graduateDate",
    "MATRICULATION_DT": "matriculationDate",
    "DEGREE_CD": "degreeCode",
    "NSC_IND": "nscIndicator"
}

ABMS_COLUMNS = {
    "CERT_BOARD": "certificateBoard",
    "CERTIFICATE": "certificate",
    "CERTIFICATE_TYPE": "certificateType",
    "EFFECTIVE_DT": "effectiveDate",
    "EXPIRATION_DT": "expirationDate",
    "LAST_REPORTED_DT": "lastReportedDate",
    "REACTIVATION_DT": "reverificationDate",
    "CERT_STAT_DESC": "certificateStatusDescription",
    "DURATION_TYPE_DESC": "durationTypeDescription",
    "MOC_MET_RQT": "meetingMOC",
    "ABMS_RECORD_TYPE": "status"
}

MEDICAL_TRAINING_COLUMNS = {
    "PRIMARY_SPECIALITY": "primarySpecialty",
    "INST_NAME": "institutionName",
    "INST_STATE": "institutionState",
    "BEGIN_DT": "beginDate",
    "END_DT": "endDate",
    "CONFIRM_STATUS": "confirmStatus",
    "INC_MSG": "incMsg",
    "PROGRAM_NM": "programName",
    "TRAINING_TYPE": "trainingType"
}

LICENSES_COLUMNS = {
    "LIC_ISSUE_DT": "issueDate",
    "LIC_EXP_DT": "expirationDate",
    "LIC_AS_OF_DT": "lastReportedDate",
    "LIC_TYPE_DESC": "typeDescription",
    "LIC_STATE_DESC": "stateDescription",
    "DEGREE_CD": "degreeCode",
    "LIC_STATUS_DESC": "licenseStatusDescription",
    "LIC_NBR": "licenseNumber",
    "LIC_RNW_DT": "renewalDate",
}

LICENSE_NAME_COLUMNS ={
    "FIRST_NAME": "firstName",
    "MIDDLE_NAME": "middleName",
    "LAST_NAME": "lastName",
    "RPTD_SFX_NM": "suffix",
    "RPTD_FULL_NM": "fullReportedName"
}

SANCTIONS_COLUMNS = [
    "medicareMedicaidSanction",
    "federalSanctions",
    "additionalSanction",
    "stateSanctions",
    "deaSanction",
    "dodSanction",
    "airforceSanction",
    "armySanction",
    "navySanction",
    "vaSanction",
]

SANCTION_VALUE_COLUMNS = [
    "medicareMedicaidSanctionValue",
    "additionalSanctionValue",
    "stateSanctionsValue",
    "deaSanctionValue",
    "dodSanctionValue",
    "airforceSanctionValue",
    "armySanctionValue",
    "navySanctionValue",
    "vaSanctionValue",
]

MPA_COLUMNS = {
    "MPA_DESC": "description"
}

ECFMG_COLUMNS = {
    "ECFMG_NBR": "applicantNumber"
}

ME_NUMBER_COLUMNS = {
    "ENTITY_ID": "entityId",
    "ME_NBR": "meNumber"
}

AGGREGATED_COLUMNS = [
    "demographics",
    "dea",
    "practiceSpecialties",
    "npi",
    "medicalSchools",
    "abms",
    "medicalTraining",
    "licenses",
    "sanctions",
    "mpa",
    "ecfmg",
    "meNumber"
]
