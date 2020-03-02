/*****************************************************************************************************/
/********************************* Global Variable Assignment Section ********************************/
/*****************************************************************************************************/

/* Create global variable for path of validation data spreadsheet */
%macro in_path;
	%global in_file;
	%let in_file = 'U:\Source Files\Data Analytics\Baseline\data\PhysicianProfessionalDataFile_20190810_180157410'; 
%mend in_path;

/* Create global variable for output path to save combined data */
%macro out_path;
	%global out_file;
	%let out_file = 'U:\Source Files\Data Analytics\Data-Science\Data\PPD\ppd_data_20190810.csv'; 
%mend out_path;

/* Path to save output SAS file */
%macro sas_out_path;
	%global sas_path;
	%let sas_path = 'U:\Source Files\Data Analytics\Data-Science\Data\PPD\'; 
%mend sas_out_path;

/* Path to save output SAS file */
%macro sas_file_name;
	%global sas_file;
	%let sas_file = 'U:\Source Files\Data Analytics\Data-Science\Data\PPD\ppd_data_20190810.sas7bdat'; 
%mend sas_file_name;


/*****************************************************************************************************/
/************************************** Code Execution Section ***************************************/
/*****************************************************************************************************/

/* Import PPD file in correct format */
Data ppd_data;
	infile %in_path &in_file
	delimiter = '|' MISSOVER DSD lrecl=32767 ;
		informat ME $11. ;
		informat RECORD_ID $1. ;
		informat UPDATE_TYPE $1. ;
		informat ADDRESS_TYPE $1. ;
		informat MAILING_NAME $40. ;
		informat LAST_NAME $35. ;
		informat FIRST_NAME $35. ;
		informat MIDDLE_NAME $35. ;
		informat SUFFIX $1. ;
		informat MAILING_LINE_1 $80. ;
		informat MAILING_LINE_2 $80. ;
		informat CITY $30. ;
		informat STATE $2. ;
		informat ZIP $5. ;
		informat SECTOR $4. ;
		informat CARRIER_ROUTE $5. ;
		informat ADDRESS_UNDELIVERABLE_FLAG $1. ;
		informat FIPS_COUNTY $3. ;
		informat FIPS_STATE $2. ;
		informat PRINTER_CONTROL_CODE $1. ;
		informat PC_ZIP $5. ;
		informat PC_SECTOR $4. ;
		informat DELIVERY_POINT_CODE $2. ;
		informat CHECK_DIGIT $1. ;
		informat PRINTER_CONTROL_CODE_2 $1. ;
		informat REGION $1. ;
		informat DIVISION $1. ;
		informat GROUP $1. ;
		informat TRACT $4. ;
		informat SUFFIX_CENSUS $2. ;
		informat BLOCK_GROUP $1. ;
		informat MSA_POPULATION_SIZE $1. ;
		informat MICRO_METRO_IND $1.;
		informat CBSA $5. ;
		informat CBSA_DIV_IND $1.;
		informat MD_DO_CODE $1. ;
		informat BIRTH_YEAR $4. ;
		informat BIRTH_CITY $25. ;
		informat BIRTH_STATE $2. ;
		informat BIRTH_COUNTRY $3. ;
		informat GENDER $1. ;
		informat TELEPHONE_NUMBER $10. ;
		informat PRESUMED_DEAD_FLAG $1. ;
		informat FAX_NUMBER $10. ;
		informat TOP_CD $3. ;
		informat PE_CD $3. ;
		informat PRIM_SPEC_CD $3. ;
		informat SEC_SPEC_CD $3. ;
		informat MPA_CD $3. ;
		informat PRA_RECIPIENT $1. ;
		informat PRA_EXP_DT $10. ;
		informat GME_CONF_FLG $1. ;
		informat FROM_DT $10. ;
		informat TO_DT $10. ;
		informat YEAR_IN_PROGRAM $2. ;
		informat POST_GRADUATE_YEAR $2. ;
		informat GME_SPEC_1 $3. ;
		informat GME_SPEC_2 $3. ;
		informat TRAINING_TYPE $1. ;
		informat GME_INST_STATE $2. ;
		informat GME_INST_ID $4. ;
		informat MEDSCHOOL_STATE $3. ;
		informat MEDSCHOOL_ID $2. ;
		informat MEDSCHOOL_GRAD_YEAR $4. ;
		informat NO_CONTACT_IND $1. ;
		informat NO_WEB_FLAG $1. ;
		informat PDRP_FLAG $1. ;
		informat PDRP_START_DT $10. ;
		informat POLO_MAILING_LINE_1 $80. ;
		informat POLO_MAILING_LINE_2 $80. ;
		informat POLO_CITY $30. ;
		informat POLO_STATE $2. ;
		informat POLO_ZIP $5. ;
		informat POLO_SECTOR $4. ;
		informat POLO_CARRIER_ROUTE $5. ;
		informat MOST_RECENT_FORMER_LAST_NAME $35. ;
		informat MOST_RECENT_FORMER_MIDDLE_NAME $35. ;
		informat MOST_RECENT_FORMER_FIRST_NAME $35. ;
		informat NEXT_MOST_RECENT_FORMER_LAST $35. ;
		informat NEXT_MOST_RECENT_FORMER_MIDDLE $35. ;
		informat NEXT_MOST_RECENT_FORMER_FIRST $35. ;
			format ME $11. ;
			format RECORD_ID $1. ;
			format UPDATE_TYPE $1. ;
			format ADDRESS_TYPE $1. ;
			format MAILING_NAME $40. ;
			format LAST_NAME $35. ;
			format FIRST_NAME $35. ;
			format MIDDLE_NAME $35. ;
			format SUFFIX $1. ;
			format MAILING_LINE_1 $80. ;
			format MAILING_LINE_2 $80. ;
			format CITY $30. ;
			format STATE $2. ;
			format ZIP $5. ;
			format SECTOR $4. ;
			format CARRIER_ROUTE $5. ;
			format ADDRESS_UNDELIVERABLE_FLAG $1. ;
			format FIPS_COUNTY $3. ;
			format FIPS_STATE $2. ;
			format PRINTER_CONTROL_CODE $1. ;
			format PC_ZIP $5. ;
			format PC_SECTOR $4. ;
			format DELIVERY_POINT_CODE $2. ;
			format CHECK_DIGIT $1. ;
			format PRINTER_CONTROL_CODE_2 $1. ;
			format REGION $1. ;
			format DIVISION $1. ;
			format GROUP $1. ;
			format TRACT $4. ;
			format SUFFIX_CENSUS $2. ;
			format BLOCK_GROUP $1. ;
			format MSA_POPULATION_SIZE $1. ;
			format MICRO_METRO_IND $1.;
			format CBSA $5. ;
			format CBSA_DIV_IND $1.;
			format MD_DO_CODE $1. ;
			format BIRTH_YEAR $4. ;
			format BIRTH_CITY $25. ;
			format BIRTH_STATE $2. ;
			format BIRTH_COUNTRY $3. ;
			format GENDER $1. ;
			format TELEPHONE_NUMBER $10. ;
			format PRESUMED_DEAD_FLAG $1. ;
			format FAX_NUMBER $10. ;
			format TOP_CD $3. ;
			format PE_CD $3. ;
			format PRIM_SPEC_CD $3. ;
			format SEC_SPEC_CD $3. ;
			format MPA_CD $3. ;
			format PRA_RECIPIENT $1. ;
			format PRA_EXP_DT $10. ;
			format GME_CONF_FLG $1. ;
			format FROM_DT $10. ;
			format TO_DT $10. ;
			format YEAR_IN_PROGRAM $2. ;
			format POST_GRADUATE_YEAR $2. ;
			format GME_SPEC_1 $3. ;
			format GME_SPEC_2 $3. ;
			format TRAINING_TYPE $1. ;
			format GME_INST_STATE $2. ;
			format GME_INST_ID $4. ;
			format MEDSCHOOL_STATE $3. ;
			format MEDSCHOOL_ID $2. ;
			format MEDSCHOOL_GRAD_YEAR $4. ;
			format NO_CONTACT_IND $1. ;
			format NO_WEB_FLAG $1. ;
			format PDRP_FLAG $1. ;
			format PDRP_START_DT $10. ;
			format POLO_MAILING_LINE_1 $80. ;
			format POLO_MAILING_LINE_2 $80. ;
			format POLO_CITY $30. ;
			format POLO_STATE $2. ;
			format POLO_ZIP $5. ;
			format POLO_SECTOR $4. ;
			format POLO_CARRIER_ROUTE $5. ;
			format MOST_RECENT_FORMER_LAST_NAME $35. ;
			format MOST_RECENT_FORMER_MIDDLE_NAME $35. ;
			format MOST_RECENT_FORMER_FIRST_NAME $35. ;
			format NEXT_MOST_RECENT_FORMER_LAST $35. ;
			format NEXT_MOST_RECENT_FORMER_MIDDLE $35. ;
			format NEXT_MOST_RECENT_FORMER_FIRST $35. ;
	input
		ME $
		RECORD_ID $
		UPDATE_TYPE $
		ADDRESS_TYPE $
		MAILING_NAME $ 
		LAST_NAME $
		FIRST_NAME $ 
		MIDDLE_NAME $ 
		SUFFIX $
		MAILING_LINE_1 $
		MAILING_LINE_2 $
		CITY $
		STATE $ 
		ZIP $
		SECTOR $ 
		CARRIER_ROUTE $
		ADDRESS_UNDELIVERABLE_FLAG $
		FIPS_COUNTY $
		FIPS_STATE $ 
		PRINTER_CONTROL_CODE $ 
		PC_ZIP $
		PC_SECTOR $ 
		DELIVERY_POINT_CODE $ 
		CHECK_DIGIT $
		PRINTER_CONTROL_CODE_2 $
		REGION $
		DIVISION $ 
		GROUP $
		TRACT $ 
		SUFFIX_CENSUS $ 
		BLOCK_GROUP $ 
		MSA_POPULATION_SIZE $
		MICRO_METRO_IND $
		CBSA $
		CBSA_DIV_IND $
		MD_DO_CODE $
		BIRTH_YEAR $
		BIRTH_CITY $ 
		BIRTH_STATE $ 
		BIRTH_COUNTRY $ 
		GENDER $
		TELEPHONE_NUMBER $
		PRESUMED_DEAD_FLAG $ 
		FAX_NUMBER $
		TOP_CD $
		PE_CD $ 
		PRIM_SPEC_CD $
		SEC_SPEC_CD $ 
		MPA_CD $
		PRA_RECIPIENT $
		PRA_EXP_DT $ 
		GME_CONF_FLG $ 
		FROM_DT $ 
		TO_DT $ 
		YEAR_IN_PROGRAM $
		POST_GRADUATE_YEAR $ 
		GME_SPEC_1 $
		GME_SPEC_2 $
 		TRAINING_TYPE $
		GME_INST_STATE $ 
		GME_INST_ID $
		MEDSCHOOL_STATE $ 
		MEDSCHOOL_ID $
		MEDSCHOOL_GRAD_YEAR $ 
		NO_CONTACT_IND $
		NO_WEB_FLAG $
		PDRP_FLAG $
		PDRP_START_DT $ 
		POLO_MAILING_LINE_1 $ 
		POLO_MAILING_LINE_2 $ 
		POLO_CITY $
		POLO_STATE $ 
		POLO_ZIP $
		POLO_SECTOR $ 
		POLO_CARRIER_ROUTE $ 
		MOST_RECENT_FORMER_LAST_NAME $
		MOST_RECENT_FORMER_MIDDLE_NAME $
		MOST_RECENT_FORMER_FIRST_NAME $
		NEXT_MOST_RECENT_FORMER_LAST $
		NEXT_MOST_RECENT_FORMER_MIDDLE $
		NEXT_MOST_RECENT_FORMER_FIRST $
	;
Run;

/** 12/30/2017 file has 1,219,259 records **/
proc sql;
	select count (distinct ME) from ppd_data;
quit; 


/************************************************************************/
/* Save to csv file */

/* Save the dataset with status variables to a csv file for use in analysis */
filename out_name %out_path &out_file encoding = "utf-8";

proc export data = ppd_data 
	outfile = out_name 
	dbms = csv 
	replace;
run;


/************************************************************************/
/* Save to sas7bdat file */

libname out %sas_out_path &sas_path;

/* Path to save output SAS file */
%macro old_out_path;
	%global old_name;
	%let old_name = 'C:\AMA Sandbox\Common Data\PPD\ppd_data.sas7bdat'; 
%mend old_out_path;

proc copy in = work out = out;
	select ppd_data;
run;
quit;

data _null_;
	rc = rename(%old_out_path &old_name, %sas_file_name &sas_file , 'file');
run;

