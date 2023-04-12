"""SNOMED CPT Transformer"""
from   collections import defaultdict
import json
import logging
import re

import pandas

from   datalabs.task import Task


logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class SNOMEDMappingTransformerTask(Task):
    def run(self):
        LOGGER.debug(self._data)

        parsed_data = pandas.read_excel(self._data[0])

        cleaned_data = self._clean_data(parsed_data)

        renamed_data = self._rename_columns(cleaned_data)

        mappings, mapped_data = self._generate_cpt_mappings(renamed_data)

        mappings = self._generate_keyword_mappings(mapped_data, mappings)

        return [json.dumps(mappings).encode()]

    def _clean_data(self, data):
        self._fill_missing_ids(data)

        self._set_default_descriptor_values(data)

        return data

    @classmethod
    def _fill_missing_ids(cls, data):
        data.loc[:, "Concept Id"] = data["Concept Id"].fillna(method='ffill').astype('int').astype('str')

        data.loc[:, "FSN"] = data["FSN"].fillna(method='ffill')

    @classmethod
    def _set_default_descriptor_values(cls, data):
        data.loc[:, "FSN"] = data["FSN"].astype('str')
        data.loc[data["FSN"] == "nan", "FSN"] = ""

        data["CPT Descriptor"] = data["CPT Descriptor"].astype('str')
        data.loc[data["CPT Descriptor"] == "nan", "CPT Descriptor"] = ""

    @classmethod
    def _rename_columns(cls, data):
        renamed_data = data[["Concept Id", "FSN", "Map Category", "CPT Code", "CPT Descriptor", "Map Id"]].rename(
            columns={
                "FSN": "snomed_descriptor",
                "Map Category": "map_category",
                "CPT Descriptor": "cpt_descriptor",
                "Map Id": "map_id"
            }
        )

        return renamed_data

    def _generate_cpt_mappings(self, data):

        mappings = []
        cpt_mappings = self._create_cpt_mappings(data)

        self._generate_cpt_items(mappings, cpt_mappings)

        return mappings, cpt_mappings

    @classmethod
    def _create_cpt_mappings(cls, data):
        data.loc[:, "pk"] = "CONCEPT:" + data["Concept Id"]

        data.loc[data["map_category"] == "Unmappable", "sk"] = "UNMAPPABLE:" + data.loc[data["map_category"] == "Unmappable", "map_id"].astype('str')
        data.loc[~(data["map_category"] == "Unmappable"), "sk"] = "CPT:" + data.loc[~(data["map_category"] == "CPT"), "CPT Code"].astype(str)

        data = data.drop_duplicates(subset=("pk", "sk"))

        mapped_data = data.loc[:, ["sk", "pk", "snomed_descriptor", "map_category", "cpt_descriptor"]]

        return mapped_data

    @classmethod
    def _generate_cpt_items(cls, mappings, cpt_mappings):

        for index in range(len(cpt_mappings)):
            row = cpt_mappings.iloc[index]
            mappings.append(row.to_dict())

    def _generate_keyword_mappings(self, data, mappings):
        keywords_mapping = self._create_keyword_mappings(data)

        self._generate_keyword_items(mappings, keywords_mapping)

        return mappings

    @classmethod
    def _create_keyword_mappings(cls, data):
        data["keyword"] = data.snomed_descriptor.apply(lambda x: re.sub(r'[^\w ]+', '', x)).str.lower().str.split()

        keyword_mappings = data.loc[:, ["pk", "sk", "keyword"]].explode("keyword").reset_index(drop=True).drop_duplicates()
        data.drop(columns="keyword")

        return keyword_mappings

    @classmethod
    def _generate_keyword_items(cls, mappings, keywords_mapping):
        mappings += [
            dict(pk=f"{row.pk}:{row.sk}", sk=f"KEYWORD:{row.keyword}")
            for index, row in keywords_mapping.iterrows() if row.sk.startswith("CPT:")
        ]
