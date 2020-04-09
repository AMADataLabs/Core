import settings
import pandas as pd
from datalabs.access.edw import EDW
with EDW() as edw:
    data = edw.read("select distinct b.party_id, b.first_nm, b.middle_nm, b.last_nm, c.me_number \
                    from amaedw.party_cat a \
                    left outer join amaedw.person_nm b \
                    on a.party_id=b.party_id \
                    left outer join (select distinct party_id, key_val as me_number from amaedw.party_key where key_type_id=18 and active_ind='Y') c on a.party_id=c.party_id where a.cat_grp_id = 482 and a.cat_cd_id = 6664 and a.src_end_dt is null " )

print(data.head())