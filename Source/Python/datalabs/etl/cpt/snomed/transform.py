"""SNOMED CPT Transformer"""
import json
from   collections import defaultdict

import hashlib
import logging
import re

from   datalabs.access.aws import AWSClient
from   datalabs.task import Task

import pandas


logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class SNOMEDMappingTransformerTask(Task):
    def run(self):
        LOGGER.debug(self._data)

        parsed_data = self._parse()
        processed_data = self._process_columns(parsed_data)
        json_data = self._csv_to_json(processed_data)

        return [json_data.encode()]

    def _parse(self):
        data_sheet = pandas.read_excel(self._data[0])
        parsed_data = data_sheet[["Concept Id", "FSN", "Map Category", "CPT Code", "CPT Descriptor", "Map Id"]].rename(
            columns={
                "Concept Id": "pk",
                "CPT Code": "sk",
                "FSN": "snomed_descriptor",
                "Map Category": "map_category",
                "CPT Descriptor": "cpt_descriptor",
                "Map Id": "map_id"
            }
        )

        return parsed_data

    def _process_columns(self, data):
        data["pk"] = data["pk"].fillna(method='ffill')
        data.loc[:, "pk"] = "CONCEPT:" + data.pk.astype('int').astype('str')
        data.loc[data.map_category == "Unmappable", "sk"] = "UNMAPPABLE:" + data.loc[
            data.map_category == "Unmappable", "map_id"].astype('str')
        data.loc[~(data.map_category == "Unmappable"), "sk"] = "CPT:" + data.loc[
            ~(data.map_category == "CPT"), "sk"].astype(str)
        data.snomed_descriptor = data.snomed_descriptor.astype('str')
        data.loc[data.snomed_descriptor == "nan", "snomed_descriptor"] = ""
        data.cpt_descriptor = data.cpt_descriptor.astype('str')
        data.loc[data.cpt_descriptor == "nan", "cpt_descriptor"] = ""
        data["clean_descriptor"] = data.cpt_descriptor.apply(
            lambda x: re.sub(r'[^\w ]+', '', x)).str.lower().str.split()
        processed_data = data.drop_duplicates(subset=("pk", "sk"))

        return processed_data

    def _csv_to_json(self, data):
        mappings = []

        keywords = data[["pk", "clean_descriptor"]].rename(columns={"clean_descriptor": "keywords"})
        snomed = data.drop(columns=["clean_descriptor", "map_id"])

        keyword_map = defaultdict(list)

        for index in range(len(keywords)):
            for keyword in keywords.iloc[index].keywords:
                keyword_map[keyword].append(keywords.iloc[index].pk)

        keyword_map = {keyword: set(pks) for keyword, pks in keyword_map.items()}

        for index in range(len(snomed)):
            row = snomed.iloc[index]
            mappings.append(row.to_dict())

        for keyword, pks in keyword_map.items():
            for pk in pks:
                mappings.append(dict(pk=pk, sk=f"KEYWORD:{keyword}"))

        return json.dumps(mappings)
