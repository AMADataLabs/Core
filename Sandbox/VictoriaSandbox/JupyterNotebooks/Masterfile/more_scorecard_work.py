#Import dependencies:
import pandas as pd
import pyodbc
from auth import username, password_aims, password_edw
import numpy as np


#Connect to databases
s = "DSN=PRDDW; UID={}; PWD={}".format(username, password_edw)
v = 'DSN=aims_prod; UID={}; PWD={}'.format(username, password_aims)
m = 'DSN=PRDDM; UID={}; PWD={}'.format(username, password_edw)
AMAEDW = pyodbc.connect(s)
AIMS_conn = pyodbc.connect(v)
AMADM = pyodbc.connect(m)
AIMS_conn.execute('SET ISOLATION TO DIRTY READ;')



*using code from membership team, pull the list of physicians with a current email address;
proc sql;
create table mbrshp_email_list as
select d.*, f.sts_id
from amadm.dim_physician d, amadm.fact_mbrshp_hist f 
where d.person_id = f.person_id and d.current_ind = "Y" and d.is_seed_account = "N" and f.mbrshp_yr = year(today())
	and f.effective_begin_dt <= today() and f.effective_end_dt >= today() and d.email_status is not null;
quit;

*add the ME number to table;
proc sql;
create table mbrshp_email_list2 as
select m.*, p.me 
from mbrshp_email_list m join edw.party_id_to_me_vw p on m.party_id = p.party_id;
quit;

*Add entity id to the table;
proc sql;
create table mbrshp_email_list3 as
select m.*, p.entity_id 
from mbrshp_email_list2 m join edw.party_entity_vw p on m.party_id = p.party_id;
quit;

*Add the email details to the table (adding purpose_type, cat_cd, etc.);
proc sql;
create table mbrshp_emails as
select m.*,p.*
from mbrshp_email_list3 m join edw.party_email p on m.party_id = p.party_id
where p.thru_dt is null ;
quit;

*Add in more detail like purpose usage and purpose type description;
proc sql;
create table mbrshp_emails2 as 
select m.*, c.purpose_type_cd, c.purpose_type_desc, c.purpose_usg_cd, c.purpose_usg_desc
from mbrshp_emails m join edw.cont_purpose_type c on m.purpose_type_id = c.purpose_type_id;
quit;


proc sql;
create table mbrshp_emails_pref as
select * from mbrshp_emails2 where purpose_usg_cd = "PE";
quit;

*add in the email address from EDW;
proc sql;
create table mbrshp_emails_pref2 as
select m.*, e.email_addr 
from mbrshp_emails_pref m join edw.email_addr e on m.email_id = e.email_id;
quit;

*keep the records where the email from the membership table matches email from edw table;
data mbrshp_emails_pref3;
set mbrshp_emails_pref2;
if pref_email = email_addr then email_match = "Y";
else email_match = "N";
if email_match = "Y";
run;

proc sql;
select count(distinct party_id) from mbrshp_emails_pref3;
quit;

*add in the category code and description;
proc sql;
create table mbrshp_emails_pref4 as
select m.*, c.category_code, c.desc, c.src_sys
from mbrshp_emails_pref3 m left join edw.cat_cd c on m.cat_cd_id = c.cat_cd_id;
quit;

proc freq data = mbrshp_emails_pref4;
table category_code src_sys;
run;

*dedup the table and keep only the most recent record for each physician;
proc sort data = mbrshp_emails_pref4;
by party_id;
run;
data mbrshp_emails_pref4_dedup;
set mbrshp_emails_pref4;
by party_id;
if first.party_id;
run;

proc freq data = mbrshp_emails_pref4_dedup;
table category_code src_sys;
run;

*reformatting the begin date of email;
data mbrshp_emails_pref5;
set mbrshp_emails_pref4_dedup;
email_date = datepart(from_dt);
format email_date MMDDYY10.;
run;




/******************************************************************************************************************/

***SAVE A COPY OF THE CURRENT PREFERRED EMAILS FOR THE MONTH - NEED TO USE IN NEXT MONTH TO GET NET LIFT!!***;


/** YY  *************May run aprall_may02   June run Mayll_jun02 ***********************
data emailsc.emails_aprall_may02; 
data emailsc.emails_mayall_jun02; 
data emailsc.emails_junall_Jul02;
data emailsc.emails_julall_Aug02; 
data emailsc.emails_Augall_Sep02; 
data emailsc.emails_Sepall_Oct02;*/
data emailsc.emails_Octall_Nov02;
set mbrshp_emails_pref5;
run;

*Look only at emails with a date during previous month;
proc sql;
create table mbrshp_emails_pref5_new as
select * from mbrshp_emails_pref5  /*
where email_date >= '01Apr2019'd and email_date <= '30Apr2019'd;  YY <=  May 
where email_date >= '01May2019'd and email_date <= '31May2019'd;  
where email_date >= '01Jun2019'd and email_date <= '30Jun2019'd; 
where email_date >= '01Jul2019'd and email_date <= '31Jul2019'd; 
where email_date >= '01Aug2019'd and email_date <= '31Aug2019'd; 
where email_date >= '01Sep2019'd and email_date <= '30Sep2019'd; */
where email_date >= '01Oct2019'd and email_date <= '31Oct2019'd;
quit;


*Add in entity id to records;
proc sql;
create table mbrshp_emails_pref6_new as
select m.*, e.entity_id as entity_id2 "entity_id2" 
from mbrshp_emails_pref5_new m join aimsprod.entity_key_et e on m.me = e.key_type_val
where key_type = "ME";
quit;

*Get the net lift records by removing those from the previous month's full table of preferred emails;
proc sql;
create table netlifts as
select * from mbrshp_emails_pref5_new /*
where entity_id not in (select entity_id from emailsc.emails_marall_apr02);  <= may run  YY  
where entity_id not in (select entity_id from emailsc.emails_aprall_may02);  
where entity_id not in (select entity_id from emailsc.emails_mayall_jun02);  
where entity_id not in (select entity_id from emailsc.emails_junall_jul02);  
where entity_id not in (select entity_id from emailsc.emails_julall_Aug02);  
where entity_id not in (select entity_id from emailsc.emails_Augall_Sep02);  */
where entity_id not in (select entity_id from emailsc.emails_Sepall_Oct02);
quit;

*Look at frequency of category codes from net lifts;
*This frequency breakdown is what will be used in the scorecard;
proc freq data = netlifts;
table category_code;
run;

*Save a copy of the netlifts;
/*
data emailsc.emails_netlift_apr_may02;  <= May run change 
data emailsc.emails_netlift_may_jun02;
data emailsc.emails_netlift_jun_jul02; 
data emailsc.emails_netlift_jul_Aug02; 
data emailsc.emails_netlift_aug_Sep02; 
data emailsc.emails_netlift_sep_Oct02; */
data emailsc.emails_netlift_oct_Nov02;
set netlifts;
run;


/***********************************************************/
/****  3,445 not in PPD in August file mostly resident  ****/
/************

proc sql;
create table emailsc.MEnotinppd as  
select * from emailsc.emails_netlift_aug_sep02
where MED_EDU_NBR not in (select me from ppd.new_ppd);

******/
