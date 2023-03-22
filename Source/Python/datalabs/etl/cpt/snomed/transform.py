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

        processed_data = self._process_data(parsed_data)
        renamed_data = self._rename_columns(processed_data)

        json_data = self._csv_to_json(renamed_data)

        return [json_data.encode()]

    def _process_data(self, data):
        self._fill_missing_ids(data)

        self._create_sorting_key(data)

        self._set_default_descriptor_values(data)

        processed_data = data.drop_duplicates(subset=("Concept Id", "CPT Code"))

        return processed_data

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

    def _csv_to_json(self, data):
        mappings = []
        keyword_map = defaultdict(list)

        data, keywords = self._create_keywords(data)

        keywords, keyword_map = self._create_keyword_mappings(keywords, keyword_map)
        keywords, keyword_map = self._create_reverse_mappings(keywords, keyword_map)

        mappings = self._generate_mapping_table(mappings, data)
        mappings = self._generate_keyword_table(mappings, keyword_map)

        return json.dumps(mappings)

    @classmethod
    def _create_keywords(cls, data):
        data["clean_descriptor"] = data.cpt_descriptor.apply(
            lambda x: re.sub(r'[^\w ]+', '', x)).str.lower().str.split()

        keywords = data[["pk", "clean_descriptor"]].rename(columns={"clean_descriptor": "keywords"})
        data = data.drop(columns=["clean_descriptor", "map_id"])

        return data, keywords

    @classmethod
    def _create_keyword_mappings(cls, keywords, keyword_map):
        for index in range(len(keywords)):
            for keyword in keywords.iloc[index].keywords:
                keyword_map[keyword].append(keywords.iloc[index].pk)

        return keywords, keyword_map

    @classmethod
    def _create_reverse_mappings(cls, keywords, keyword_map):
        keyword_map = {keyword: set(pks) for keyword, pks in keyword_map.items()}

        return keywords, keyword_map

    @classmethod
    def _generate_mapping_table(cls, mappings, data):
        for index in range(len(data)):
            row = data.iloc[index]
            mappings.append(row.to_dict())

        return mappings

    @classmethod
    def _generate_keyword_table(cls, mappings, keyword_map):
        for keyword, pks in keyword_map.items():
            for pk in pks:
                mappings.append(dict(pk=pk, sk=f"KEYWORD:{keyword}"))

        return mappings
