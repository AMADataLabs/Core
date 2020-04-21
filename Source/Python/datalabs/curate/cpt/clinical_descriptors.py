"""Clinical Descriptor Table module"""

import pandas as pd
import io


def parse_descriptors(clinicianDescriptor_obj):
    clinicianDescriptor_file = clinicianDescriptor_obj['Body'].read()
    df_cd = pd.read_excel(io.BytesIO(clinicianDescriptor_file), 'Sheet0', names=['concept_id', 'cpt_code', 'clinician_descriptor_id', 'clinician_descriptor'])

    return df_cd
