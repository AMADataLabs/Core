/*****************************************************************************************************/
/********************************* Global Variable Assignment Section ********************************/
/*****************************************************************************************************/
options compress=yes;
libname output 'C:\AMA Sandbox\Entity_Data';

libname aimsprod ODBC user=kpalmier password=**** datasrc =aims_prod schema=informix read_isolation_level = RU;
libname edw odbc user= kpalmier password= ****	datasrc = prddw 	schema = AMAEDW;

/* Create global variable for entity_comm_at output path to save combined data */
%macro out_ent_comm_at_path;
	%global out_ent_comm_at_file;
	%let out_ent_comm_at_file = 'C:\AMA Sandbox\Entity_Data\2019-10-16_Entity_Comm_AT.csv'; 
%mend out_ent_comm_at_path;

/* Create global variable for post_addr_at output path to save combined data */
%macro out_ent_comm_usg_at_path;
	%global out_ent_comm_usg_at_file;
	%let out_ent_comm_usg_at_file = 'C:\AMA Sandbox\Entity_Data\2019-10-16_Entity_Comm_USG_AT.csv'; 
%mend out_ent_comm_usg_at_path;

/* Create global variable for license_lt output path to save combined data */
%macro out_license_lt_path;
	%global out_license_lt_file;
	%let out_license_lt_file = 'C:\AMA Sandbox\Entity_Data\2019-10-16_License_LT.csv'; 
%mend out_license_lt_path;

/* Create global variable for entity_key_et output path to save combined data */
%macro out_entity_key_et_path;
	%global out_entity_key_et_file;
	%let out_entity_key_et_file = 'C:\AMA Sandbox\Entity_Data\2019-10-16_Entity_Key_ET.csv'; 
%mend out_entity_key_et_path;

/* Create global variable for post_addr_at output path to save combined data */
%macro out_post_addr_at_path;
	%global out_post_addr_at_file;
	%let out_post_addr_at_file = 'C:\AMA Sandbox\Entity_Data\2019-10-16_Post_Addr_AT.csv'; 
%mend out_post_addr_at_path;

/* Create global variable for phone_at output path to save combined data */
%macro out_phone_at_path;
	%global out_phone_at_file;
	%let out_phone_at_file = 'C:\AMA Sandbox\Entity_Data\2019-10-16_Phone_AT.csv'; 
%mend out_phone_at_path;

/* Create global variable for email_at output path to save combined data */
%macro out_email_at_path;
	%global out_email_at_file;
	%let out_email_at_file = 'C:\AMA Sandbox\Entity_Data\2019-10-16_Email_AT.csv'; 
%mend out_email_at_path;

/* Create global variable for entity_cat_ct output path to save combined data */
%macro out_entity_cat_ct_path;
	%global out_entity_cat_ct_file;
	%let out_entity_cat_ct_file = 'C:\AMA Sandbox\Entity_Data\2019-10-16_Entity_Cat_CT.csv'; 
%mend out_entity_cat_ct_path;

/* Create global variable for present_emp_pr output path to save combined data */
%macro out_present_emp_pr_path;
	%global out_present_emp_pr_file;
	%let out_present_emp_pr_file = 'C:\AMA Sandbox\Entity_Data\2019-10-16_Present_Employment_PR.csv'; 
%mend out_present_emp_pr_path;

/* Create global variable for spec_pr output path to save combined data */
%macro out_spec_pr_path;
	%global out_spec_pr_file;
	%let out_spec_pr_file = 'C:\AMA Sandbox\Entity_Data\2019-10-16_Spec_PR.csv'; 
%mend out_spec_pr_path;

/* Create global variable for fone_zr output path to save combined data */
%macro out_fone_zr_path;
	%global out_fone_zr_file;
	%let out_fone_zr_file = 'C:\AMA Sandbox\Entity_Data\2019-10-28_EDW_Fone_ZR.csv'; 
%mend out_fone_zr_path;


/*****************************************************************************************************/
/************************************** Code Execution Section ***************************************/
/*****************************************************************************************************/

/* This was the original query attempted.  This took several hours and was unable to finish
due to a connection loss during the nightly EDW/AIMS updating.  Left here for reference only */
/*
proc sql;
CREATE TABLE ent_comm_addrs AS
SELECT e.entity_id, e.comm_type, e.comm_cat, e.begin_dt, e.comm_id, e.end_dt, 
e.src_category, e.src_cat_code, 
u.comm_cat as usg_comm_cat, u.comm_usage as usg_comm_usage, u.usg_begin_dt,  
u.comm_id as usg_comm_id, u.comm_type as usg_comm_type, u.end_dt as usg_end_dt, 
u.src_cat_code as usg_src_cat_code, p.addr_line2, p.addr_line1, p.city_cd, 
p.state_cd, p.zip, p.plus4 
FROM aimsprod.entity_comm_at e
LEFT OUTER JOIN aimsprod.entity_comm_usg_at u
    ON e.entity_id = u.entity_id 
    AND e.comm_id = u.comm_id
INNER JOIN aimsprod.post_addr_at p
    ON e.comm_id = p.comm_id
WHERE e.comm_cat = 'A';
quit;
*/

/************************************************************************/
/* Save entity_comm_at table to csv file */

DATA latest_entity_comm_at;
SET aimsprod.entity_comm_at;
RUN;

/* Save the dataset with status variables to a csv file for use in analysis */
filename out_name %out_ent_comm_at_path &out_ent_comm_at_file encoding = "utf-8";

proc export data = latest_entity_comm_at 
	outfile = out_name 
	dbms = csv 
	replace;
run;


/************************************************************************/
/* Save entity_comm_usg_at table to csv file */

DATA latest_entity_comm_usg_at;
SET aimsprod.entity_comm_usg_at;
RUN;

/* Save the dataset with status variables to a csv file for use in analysis */
filename out_name %out_ent_comm_usg_at_path &out_ent_comm_usg_at_file encoding = "utf-8";

proc export data = latest_entity_comm_usg_at 
	outfile = out_name 
	dbms = csv 
	replace;
run;


/************************************************************************/
/* Save license_lt table to csv file */

DATA latest_license_lt;
SET aimsprod.license_lt;
RUN;

/* Save the dataset with status variables to a csv file for use in analysis */
filename out_name %out_license_lt_path &out_license_lt_file encoding = "utf-8";

proc export data = latest_license_lt 
	outfile = out_name 
	dbms = csv 
	replace;
run;


/************************************************************************/
/* Save entity_key_et table to csv file */

DATA latest_entity_key_et;
SET aimsprod.entity_key_et;
RUN;

/* Save the dataset with status variables to a csv file for use in analysis */
filename out_name %out_entity_key_et_path &out_entity_key_et_file encoding = "utf-8";

proc export data = latest_entity_key_et 
	outfile = out_name 
	dbms = csv 
	replace;
run;


/************************************************************************/
/* Save post_addr_at table to csv file */

DATA latest_post_addr_at;
SET aimsprod.post_addr_at;
RUN;

/* Save the dataset with status variables to a csv file for use in analysis */
filename out_name %out_post_addr_at_path &out_post_addr_at_file encoding = "utf-8";

proc export data = latest_post_addr_at 
	outfile = out_name 
	dbms = csv 
	replace;
run;


/************************************************************************/
/* Save phone_at table to csv file */

DATA latest_phone_at;
SET aimsprod.phone_at;
RUN;

/* Save the dataset with status variables to a csv file for use in analysis */
filename out_name %out_phone_at_path &out_phone_at_file encoding = "utf-8";

proc export data = latest_phone_at 
	outfile = out_name 
	dbms = csv 
	replace;
run;


/************************************************************************/
/* Save email_at table to csv file */

DATA latest_email_at;
SET aimsprod.email_at;
RUN;

/* Save the dataset with status variables to a csv file for use in analysis */
filename out_name %out_email_at_path &out_email_at_file encoding = "utf-8";

proc export data = latest_email_at 
	outfile = out_name 
	dbms = csv 
	replace;
run;

/************************************************************************/
/* Save entity_cat_ct table to csv file */

DATA latest_entity_cat_ct;
SET aimsprod.entity_cat_ct;
RUN;

/* Save the dataset with status variables to a csv file for use in analysis */
filename out_name %out_entity_cat_ct_path &out_entity_cat_ct_file encoding = "utf-8";

proc export data = latest_entity_cat_ct 
	outfile = out_name 
	dbms = csv 
	replace;
run;

/************************************************************************/
/* Save present_emp_pr table to csv file */

DATA latest_present_emp_pr;
SET aimsprod.present_emp_pr;
RUN;

/* Save the dataset with status variables to a csv file for use in analysis */
filename out_name %out_present_emp_pr_path &out_present_emp_pr_file encoding = "utf-8";

proc export data = latest_present_emp_pr 
	outfile = out_name 
	dbms = csv 
	replace;
run;

/************************************************************************/
/* Save spec_pr table to csv file */

DATA latest_spec_pr;
SET aimsprod.spec_pr;
RUN;

/* Save the dataset with status variables to a csv file for use in analysis */
filename out_name %out_spec_pr_path &out_spec_pr_file encoding = "utf-8";

proc export data = latest_spec_pr 
	outfile = out_name 
	dbms = csv 
	replace;
run;

/************************************************************************/
/* Save fone_zr table to csv file */

DATA latest_fone_zr;
SET edw.fone_zr;
RUN;

/* Save the dataset with status variables to a csv file for use in analysis */
filename out_name %out_fone_zr_path &out_fone_zr_file encoding = "utf-8";

proc export data = latest_fone_zr 
	outfile = out_name 
	dbms = csv 
	replace;
run;


