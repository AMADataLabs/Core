"""VIGNETTES CPT Transformer"""
from   io import BytesIO

import json
import logging

import pandas

from   datalabs.task import Task


logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class VignettesTransformerTask(Task):
    def run(self):
        LOGGER.debug(self._data)
        vignettes, codes, hcpcs_codes, administrative_codes = self._parse_data(self._data)

        matched_vignettes = self._match_datasets(vignettes, codes, hcpcs_codes, administrative_codes)

        cleaned_vignettes = self._clean_data(matched_vignettes)

        vignettes_mappings = self._create_vignettes_mappings(cleaned_vignettes)

        return [json.dumps(vignettes_mappings).encode()]

    @classmethod
    def _parse_data(cls, data):
        parsed_vignettes = pandas.read_csv(
            BytesIO(data[0]), delimiter='|', encoding='latin-1', skiprows=31, header=None, names=[
                'cpt_code','long_descriptor','typical_patient', 'pre_service_info','intra_service_info',
                'post_service_info', 'ruc_reviewed_date', 'survey_specialty'
                ]
            )
        parsed_codes = pandas.read_excel(data[1]).rename(
            columns={'Concept Id': 'concept_id', 'CPT Code': 'cpt_code'}
            )
        parsed_hcpcs_codes = pandas.read_csv(BytesIO(data[2]), delimiter='\t').rename(
            columns={'Concept Id': 'concept_id','HCPCS II Code': 'cpt_code'}
            )
        parsed_administrative_codes = pandas.read_excel(data[3]).rename(
            columns={'Concept Id': 'concept_id','Code': 'cpt_code'}
            )

        return parsed_vignettes, parsed_codes, parsed_hcpcs_codes, parsed_administrative_codes

    def _match_datasets(self, vignettes, codes, hcpcs_codes, administrative_codes):
        matched_vignettes = self._match_codes_to_concepts(vignettes, codes)

        matched_vignettes = self._match_hcpcs_codes_to_concepts(matched_vignettes, hcpcs_codes)

        matched_vignettes = self._match_administrative_code_to_concepts(matched_vignettes, administrative_codes)

        return matched_vignettes

    def _match_codes_to_concepts(self, data, codes):
        matched_vignettes = pandas.merge(data, codes, on='cpt_code', how='left')

        return matched_vignettes[['cpt_code','long_descriptor','typical_patient','pre_service_info',
                                  'intra_service_info', 'post_service_info','ruc_reviewed_date','survey_specialty',
                                  'concept_id']]

    def _match_hcpcs_codes_to_concepts(self, data, codes):
        unmatched_vignettes  = data[data['concept_id'].isnull()]

        matched_hcpcs_codes = pandas.merge(unmatched_vignettes, codes, on='cpt_code',how='left').rename(
            columns={'concept_id_y': 'concept_id'}).drop(columns=['concept_id_x'])
        matched_hcpcs_codes = matched_hcpcs_codes[['cpt_code','long_descriptor','typical_patient','pre_service_info',
                                                   'intra_service_info','post_service_info','ruc_reviewed_date',
                                                   'survey_specialty','concept_id']]

        matched_vignettes = pandas.concat([data.dropna(subset=['concept_id']),matched_hcpcs_codes]
                                          ).reset_index(drop=True)

        return matched_vignettes

    def _match_administrative_code_to_concepts(self, data, codes):
        unmatched_vignettes  = data[data['concept_id'].isnull()]

        matched_administrative_codes = pandas.merge(unmatched_vignettes, codes, on='cpt_code',how='left').rename(
            columns={'concept_id_y': 'concept_id'}).drop(columns=['concept_id_x'])

        matched_administrative_codes = matched_administrative_codes[['cpt_code','long_descriptor','typical_patient',
                                                                     'pre_service_info','intra_service_info',
                                                                     'post_service_info','ruc_reviewed_date',
                                                                     'survey_specialty','concept_id']]

        matched_vignettes = pandas.concat([data.dropna(subset=['concept_id']), matched_administrative_codes]
                                          ).reset_index(drop=True)

        return matched_vignettes

    def _clean_data(self, data):
        data['concept_id'] = data['concept_id'].astype('int32')
        data['concept_id'] = data['concept_id'].astype(str)

        return data

    def _create_vignettes_mappings(self, data):
        data.loc[:, 'pk'] = "CPT CODE:" + data['cpt_code']
        data.loc[:, 'sk'] = "CONCEPT:" + data['concept_id']

        mapped_data = data.loc[:, ['pk', 'sk', 'typical_patient', 'pre_service_info', 'intra_service_info',
                                   'post_service_info','ruc_reviewed_date']]

        return mapped_data.to_dict('records')
