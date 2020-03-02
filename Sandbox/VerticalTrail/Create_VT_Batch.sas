/*****************************************************************************************************/
/********************************* Global Variable Assignment Section ********************************/
/*****************************************************************************************************/

libname aimsprod odbc user = kpalmier password = **** datasrc = aims_prod schema = informix;
libname edw 		odbc user= kpalmier password= **** 	datasrc = prddw 	schema = AMAEDW;


*Get list of no contact physicians;
Proc Sql;
select count(*) from aimsprod.entity_cat_ct 
where (end_dt is null and category_code = "NO-CONTACT") or (end_dt is null and category_code = "NO-EMAIL") or (end_dt is null and category_code = "NO-RELEASE");
quit;



/* Create global variable for path of wslive csv file containing status flags */
%macro in_ppd_path;
	%global in_ppd_file;
	%let in_ppd_file = 'U:\Source Files\Data Analytics\Data-Science\Data\PPD\ppd_data_20190921.csv';
%mend in_ppd_path;

/* Create global variable for output path to save PE data */
%macro ext_out_path;
	%global ext_out_file;
	%let ext_out_file = 'C:\AMA Sandbox\Temp\2019-09-24_5K_VT_Sample.xlsx'; 
%mend ext_out_path;

/* Create global variable for output path to save PE data */
%macro int_out_path;
	%global int_out_file;
	%let int_out_file = 'C:\AMA Sandbox\Temp\2019-09-24_5K_VT_Sample_Internal.xlsx'; 
%mend int_out_path;

/* Create global variable for the number of samples */
%macro num_samples;
	%global num_smpl;
	%let num_smpl = 5000;
%mend num_samples;

/*****************************************************************************************************/
/************************************** Code Execution Section ***************************************/
/*****************************************************************************************************/

/****************************************** Import Datasets ******************************************/

/* Import data from the ppd csv that contains status flags */
proc import out = ppd
	datafile = %in_ppd_path &in_ppd_file
	dbms = csv
	replace;
	getnames = yes;
	guessingrows = 32767;
run;

*gather all DPC physicians with no phone;
proc sql;
create table ppd_dpc_nophone as
select * from ppd
where top_cd = 020 and telephone_number is null;
quit;

/* Assign ME data type to 11 characters with leading 0s to match the format in aimsprod */
data ppd_dpc_nophone_padded;
	set ppd_dpc_nophone;
	me_pad = put(ME, Z11.);
run;

*add entity id;
proc sql;
create table ppd_dpc_nophone2 as
select p.*, e.entity_id
from ppd_dpc_nophone_padded p join aimsprod.entity_key_et e on p.me_pad = e.key_type_val
where key_type = "ME";
quit;

data ppd_dpc_nophone2_temp1;
	set ppd_dpc_nophone2;
	drop ME;
run;
data ppd_dpc_nophone2_temp2;
	set ppd_dpc_nophone2_temp1;
	ME = me_pad;
run;

*Get list of no contact physicians;
Proc Sql;
Create Table NoContacts as
select * from aimsprod.entity_cat_ct 
where (end_dt is null and category_code = "NO-CONTACT") or (end_dt is null and category_code = "NO-EMAIL") or (end_dt is null and category_code = "NO-RELEASE");
quit;

*remove the no contact physicians from list of physicians to select from;
proc sql;
create table ppd_dpc_nophone3 as
select * from ppd_dpc_nophone2_temp2
where entity_id not in (select entity_id from NoContacts);
quit;

*Get license info for all physicians;
proc sql;
create table licenses as
select l.entity_id, l.state_cd, l.lic_nbr, l.lic_issue_dt, l.lic_sts, l.rptd_sts, l.lic_exp_dt, l.lic_type
from aimsprod.license_lt l where entity_id in (select entity_id from ppd_dpc_nophone3) and lic_sts = "A";
quit;

*Dedup license info;
proc sort data = licenses;
by entity_id descending lic_exp_dt;
run;
data licenses_dedup;
set licenses;
by entity_id descending lic_exp_dt;
if first.entity_id;
run;

*Add license info to data;
proc sql; 
create table ppd_dpc_nophone4 as
select P.*, L.state_cd as lic_state "lic_state", lic_nbr
from ppd_dpc_nophone3 P join licenses_dedup L on P.entity_id = L.entity_id;
quit;

*Generate sample;
proc surveyselect data = ppd_dpc_nophone4
method = srs n = %num_samples &num_smpl out = VT_Sample;
run;

/* Assign ME data type to 11 characters with leading 0s to match the format in aimsprod */
data VT_Sample_2;
	set VT_Sample;
	medschool_id_pad = put(input(medschool_id, best.), Z2.);
run;

/* Assign ME data type to 11 characters with leading 0s to match the format in aimsprod */
data VT_Sample_2_temp;
	set VT_Sample_2;
	medschool_state_pad = put(input(medschool_state,best.), Z3.);
run;

*Add medical school name;
data VT_Sample_3;
set VT_Sample_2_temp;
medschool_key = cats(medschool_state_pad,medschool_id_pad);
run;

proc sql;
create table VT_Sample_4 as
select v.*, k.party_id
from VT_Sample_3 v join edw.party_key k on v.medschool_key = k.key_val
where key_type_id = 23;
quit;
proc sql;
create table VT_Sample_5 as
select v.*, o.org_nm as MEDSCHOOL_NAME "MEDSCHOOL_NAME"
from VT_Sample_4 v join edw.org_nm o on v.party_id = o.party_id
where thru_dt is null;
quit;

*Add specialty description;
proc sql;
create table VT_Sample_6 as
select v.*, s.description as specialty "specialty"
from VT_Sample_5 v join aimsprod.spec_pr s on v.prim_spec_cd = s.spec_cd;
quit;

*Add degree type;
Data VT_Sample_7;
set VT_Sample_6;
if md_do_code = "1" then degree_type = "MD";
else if md_do_code = "2" then degree_type = "DO";
run;

*Filter out unimportant information;
Data VT_Sample_8;
retain entity_id LAST_NAME FIRST_NAME MIDDLE_NAME MEDSCHOOL_GRAD_YEAR MEDSCHOOL_NAME degree_type specialty POLO_CITY POLO_STATE POLO_ZIP lic_state lic_nbr;
set VT_Sample_7;
keep entity_id LAST_NAME FIRST_NAME MIDDLE_NAME MEDSCHOOL_GRAD_YEAR MEDSCHOOL_NAME degree_type specialty POLO_CITY POLO_STATE POLO_ZIP lic_state lic_nbr;
run;

*get all historic phone numbers for those in sample;
proc sql;
create table VT_Sample_Hist_Phone as
select e.*, strip(p.area_cd)||strip(p.exchange)||strip(p.phone_nbr) as oldphone "oldphone" 
from aimsprod.entity_comm_at e join aimsprod.phone_at p on e.comm_id = p.comm_id
where comm_cat = "P" and entity_id in (select entity_id from VT_Sample);
quit;

*keep only the distinct phone numbers for each physician in sample;
data VT_Sample_Hist_Phone2;
set VT_Sample_Hist_Phone;
phone_key = cats(entity_id,"-",oldphone);
run;
proc sort data = VT_Sample_Hist_Phone2;
by phone_key;
run;
data VT_Sample_Hist_Phone3;
set VT_Sample_Hist_Phone2;
by phone_key;
if first.phone_key;
run;

*start adding the historic phone numbers to the sample;
data VT_Sample_Hist_Phone4;
set VT_Sample_Hist_Phone3;
keep entity_id oldphone;
run;
proc sort data = VT_Sample_Hist_Phone4;
by entity_id;
run;
proc transpose data = VT_Sample_Hist_Phone4 out = VT_Sample_Hist_Phone5 (drop=_name_ _label_) prefix= oldphone;
by entity_id;
var oldphone;
run;

proc sql;
create table VT_Sample_9 as
select A.*, B.*
from VT_Sample_8 A left join VT_Sample_Hist_Phone5 B on A.entity_id = B.entity_id;
quit;

data VT_Sample_10;
set VT_Sample_9;
drop entity_id;
run;

proc export data = VT_Sample_10 
	outfile = %ext_out_path &ext_out_file 
	dbms = xlsx 
	replace;
run;

proc sql;
create table VT_Sample_11 as
select A.*, B.*
from VT_Sample_7 A left join VT_Sample_Hist_Phone5 B on A.entity_id = B.entity_id;
quit;

*Filter out unimportant information;
data VT_Sample_12;
set VT_Sample_11;
drop entity_id;
run;

proc export data = VT_Sample_12 
	outfile = %int_out_path &int_out_file 
	dbms = xlsx 
	replace;
run;
