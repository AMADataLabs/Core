""" Applies a pre-trained model to score processed address feature data """

import pandas as pd
pd.set_option('max_columns', None)
import numpy as np
import os
import pickle as pk
from datetime import datetime
from matplotlib import pyplot as plt

from sklearn.preprocessing import MinMaxScaler
from matplotlib import pyplot as plt

from xgboost import XGBClassifier
from datalabs.etl.transform import TransformerTask


REQUIRED_FEATURES = [
    'entity_comm_address_age',
    'entity_comm_active_addresses',
    'entity_comm_address_active_frequency',
    'entity_comm_src_cat_code_roster',
    'entity_comm_src_cat_code_obsolete',
    'entity_comm_src_cat_code_phone-call',
    'entity_comm_src_cat_code_ppa',
    'entity_comm_src_cat_code_other',
    'entity_comm_src_cat_code_acs',
    'entity_comm_src_cat_code_oldcc',
    'entity_comm_src_cat_code_pubs',
    'entity_comm_src_cat_code_mbshp-mail',
    'entity_comm_src_cat_code_white-mail',
    'entity_comm_src_cat_code_req-cards',
    'entity_comm_src_cat_code_ama-org',
    'entity_comm_src_cat_code_list-house',
    'entity_comm_src_cat_code_group',
    'entity_comm_src_cat_code_returned',
    'entity_comm_src_cat_code_e-mail',
    'entity_comm_src_cat_code_web',
    'entity_comm_src_cat_code_mbshp-web',
    'entity_comm_src_cat_code_internet',
    'entity_comm_src_cat_code_mrkt-rsrch',
    'entity_comm_src_cat_code_usc-outbnd',
    'entity_comm_src_cat_code_schl-hosp',
    'entity_comm_src_cat_code_gme',
    'entity_comm_src_cat_code_amc',
    'entity_comm_src_cat_code_mbshp-othr',
    'entity_comm_src_cat_code_mfload',
    'entity_comm_src_cat_code_addr-ver',
    'entity_comm_src_cat_code_res-tipon',
    'entity_comm_src_cat_code_ncoa',
    'entity_comm_src_cat_code_dea',
    'entity_comm_src_cat_code_acxiomncoa',
    'entity_comm_src_cat_code_ecf-cnvrsn',
    'entity_comm_src_cat_code_acxiomlode',
    'entity_comm_src_cat_code_admit-hos',
    'entity_comm_src_cat_code_affil-grp',
    'entity_comm_src_cat_code_cgmt',
    'entity_comm_src_cat_code_prfsol',
    'entity_comm_src_cat_code_phnsurv',
    'entity_comm_src_cat_code_pps',
    'entity_comm_src_cat_code_stu-matric',
    'entity_comm_src_cat_code_websurv',
    'entity_comm_src_cat_code_npi',
    'entity_comm_src_cat_code_federation',
    'entity_comm_src_cat_code_cme-reg',
    'entity_comm_src_cat_code_mbshp-purl',
    'entity_comm_usg_comm_id_comm_usage_counts_active_op',
    'entity_comm_usg_comm_id_comm_usage_counts_active_po',
    'entity_comm_usg_comm_id_comm_usage_counts_active_web',
    'entity_comm_usg_comm_id_comm_usage_counts_active_pp',
    'entity_comm_usg_comm_id_comm_usage_counts_active_arch',
    'entity_comm_usg_comm_id_comm_usage_counts_active_jama',
    'entity_comm_usg_comm_id_comm_usage_counts_active_mshp',
    'entity_comm_usg_comm_id_comm_usage_counts_active_bill',
    'entity_comm_usg_comm_id_comm_usage_counts_active_amc',
    'entity_comm_usg_comm_id_comm_usage_counts_active_mbr',
    'entity_comm_usg_comm_id_comm_usage_counts_active_amnw',
    'entity_comm_usg_comm_id_comm_usage_counts_history_po',
    'entity_comm_usg_comm_id_comm_usage_counts_history_web',
    'entity_comm_usg_comm_id_comm_usage_counts_history_op',
    'entity_comm_usg_comm_id_comm_usage_counts_history_pp',
    'entity_comm_usg_comm_id_comm_usage_counts_history_arch',
    'entity_comm_usg_comm_id_comm_usage_counts_history_jama',
    'entity_comm_usg_comm_id_comm_usage_counts_history_amc',
    'entity_comm_usg_comm_id_comm_usage_counts_history_mshp',
    'entity_comm_usg_comm_id_comm_usage_counts_history_bill',
    'entity_comm_usg_comm_id_comm_usage_counts_history_amnw',
    'entity_comm_usg_comm_id_comm_usage_counts_history_mbr',
    'has_newer_active_license_elsewhere',
    'has_older_active_license_elsewhere',
    'has_active_license_in_this_state',
    'years_licensed_in_this_state',
    'license_this_state_years_since_expiration',
    'humach_years_since_survey',
    'humach_never_surveyed',
    'humach_address_result_unknown',
    'humach_address_result_correct',
    'humach_address_result_incorrect',
    'triangulation_iqvia_agreement',
    'triangulation_iqvia_other',
    'triangulation_symphony_agreement',
    'triangulation_symphony_other'
 ]

class AddressScoringTransformerTask(TransformerTask):
    def _transform(self) -> 'Transformed Data':
        model = pk.loads(self._parameters['data'][0])  # must have "predict_proba" method
        aggregate_features = pd.read_csv(BytesIO(self._parameters['data'][1]), sep='|', dtype=str)
        info_cols = [
            'me',
            'entity_id',
            'comm_id',
            'address_key',
            'state_cd',
            'survey_date',
            'comments',
            'office_address_verified_updated',
            'status'
        ]
        found_info_cols = [col for col in info_cols if col in aggregate_features.columns]
        info_data = aggregate_features[found_info_cols]

        aggregate_features.set_index(found_info_cols, inplace=True)
        aggregate_features = self._scale_columns(aggregate_features)
        aggregate_features = self._resolve_null_values(aggregate_features)

        predictions = model.predict_proba(aggregate_features)
        info_data['score'] = predictions
        return [pk.dumps(info_data)]

    def _scale_columns(self, data: pd.DataFrame):
        to_scale = []
        for col in tdf.columns.values:
            if 'count' in col or 'frequency' in col or '_age' in col or 'years' in col:
                scaler = MinMaxScaler()
                scaled = scaler.fit_transform(data[[col]]).reshape(1, -1)[0]
                data[col] = scaled
        return data
    
    def _resolve_null_values(self, data: pd.DataFrame):
        fillmax = ['entity_comm_address_age', 'humach_years_since_survey']
        fillneg1 = ['license_this_state_years_since_expiration', 'years_licensed_in_this_state']
        fill1 = ['humach_never_surveyed']
        
        for col in fillneg1:
            data[col].fillna(-1, inplace=True)
        for col in fill1:
            data[col].fillna(1, inplace=True)
        
        for col in data.columns.values:
            aggregate_features[col] = aggregate_features[col].astype(float)
            
        for col in fillmax:
            mx = pop_features[col].dropna().max()
            pop_features[col].fillna(mx, inplace=True)
        
        return data

    def _resolve_feature_structure(self, data: pd.DataFrame):
        # removes any extra features generated (likely source-related columns) and sorts column order
        resolved_data = pd.DataFrame()
        resolved_data.index = data.index
        for col in REQUIRED_FEATURES:
            resolved_data[col] = data[col]
        return resolved_data
