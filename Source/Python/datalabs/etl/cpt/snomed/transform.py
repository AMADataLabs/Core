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

        mappings = self._generate_cpt_mappings(renamed_data)

        mappings = self._generate_keyword_mappings(renamed_data, mappings)

        return [json.dumps(mappings).encode()]

    def _clean_data(self, data):
        self._fill_missing_ids(data)

        self._create_sorting_key(data)

        self._set_default_descriptor_values(data)

        cleaned_data = data.drop_duplicates(subset=("Concept Id", "CPT Code"))

        return cleaned_data

    @classmethod
    def _fill_missing_ids(cls, data):
        data["Concept Id"] = data["Concept Id"].fillna(method='ffill')

        data.loc[:, "Concept Id"] = "CONCEPT:" + data["Concept Id"].astype('int').astype('str')

    @classmethod
    def _create_sorting_key(cls, data):
        data.loc[data["Map Category"] == "Unmappable", "CPT Code"] = "UNMAPPABLE:" + data.loc[
            data["Map Category"] == "Unmappable", "Map Id"].astype('str')

        data.loc[~(data["Map Category"] == "Unmappable"), "CPT Code"] = "CPT:" + data.loc[
            ~(data["Map Category"] == "CPT"), "CPT Code"].astype(str)

    @classmethod
    def _set_default_descriptor_values(cls, data):
        data["FSN"] = data["FSN"].astype('str')
        data.loc[data["FSN"] == "nan", "FSN"] = ""

        data["CPT Descriptor"] = data["CPT Descriptor"].astype('str')
        data.loc[data["CPT Descriptor"] == "nan", "CPT Descriptor"] = ""

    @classmethod
    def _rename_columns(cls, data):
        renamed_data = data[["Concept Id", "FSN", "Map Category", "CPT Code", "CPT Descriptor", "Map Id"]].rename(
            columns={
                "Concept Id": "pk",
                "CPT Code": "sk",
                "FSN": "snomed_descriptor",
                "Map Category": "map_category",
                "CPT Descriptor": "cpt_descriptor",
                "Map Id": "map_id"
            }
        )

        return renamed_data

    def _generate_cpt_mappings(self, data):
        mappings = []

        for index in range(len(data)):
            row = data.iloc[index]
            mappings.append(row.to_dict())

        return mappings

    def _generate_keyword_mappings(self, data, mappings):
        keyword_map = defaultdict(list)

        keywords = self._create_keywords(data)

        keyword_map = self._create_keyword_mappings(keywords, keyword_map)

        reverse_keyword_map = self._create_reverse_mappings(keyword_map)

        self._generate_keyword_items(mappings, reverse_keyword_map)

        return mappings

    @classmethod
    def _create_keywords(cls, data):
        data["clean_descriptor"] = data.cpt_descriptor.apply(
            lambda x: re.sub(r'[^\w ]+', '', x)).str.lower().str.split()

        keywords = data[["pk", "clean_descriptor"]].rename(columns={"clean_descriptor": "keywords"})
        data.drop(columns=["clean_descriptor", "map_id"])

        return keywords

    @classmethod
    def _create_keyword_mappings(cls, keywords, keyword_map):
        for index in range(len(keywords)):
            for keyword in keywords.iloc[index].keywords:
                keyword_map[keyword].append(keywords.iloc[index].pk)

        return keyword_map

    @classmethod
    def _create_reverse_mappings(cls, keyword_map):
        return {keyword: set(pks) for keyword, pks in keyword_map.items()}

    @classmethod
    def _generate_keyword_items(cls, mappings, keyword_map):
        for keyword, pks in keyword_map.items():
            for pk in pks:
                mappings.append(dict(pk=pk, sk=f"KEYWORD:{keyword}"))
