"""SNOMED CPT Transformer"""
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

        cpt_mappings = self._generate_cpt_mappings(renamed_data)

        keyword_mappings = self._generate_keyword_mappings(cpt_mappings)

        table_items = self._generate_table_items(cpt_mappings.drop(columns="keyword"), keyword_mappings)

        return [json.dumps(table_items).encode()]

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
        cpt_mappings = self._create_cpt_mappings(data)

        return cpt_mappings

    @classmethod
    def _create_cpt_mappings(cls, data):
        data.loc[:, "pk"] = "CONCEPT:" + data["Concept Id"]

        data.loc[
            data["map_category"] == "Unmappable", "sk"] = "UNMAPPABLE:" + data.loc[data["map_category"] == "Unmappable",
            "map_id"
        ].astype('str')

        data.loc[
            ~(data["map_category"] == "Unmappable"), "sk"] = "CPT:" + data.loc[~(data["map_category"] == "CPT"),
            "CPT Code"
        ].astype(str)

        data = data.drop_duplicates(subset=("pk", "sk"))

        mapped_data = data.loc[:, ["sk", "pk", "snomed_descriptor", "map_category", "cpt_descriptor"]]

        return mapped_data

    def _generate_keyword_mappings(self, data):
        keywords_mapping = self._create_keyword_mappings(data)

        return keywords_mapping

    @classmethod
    def _create_keyword_mappings(cls, keyword_map):
        keyword_map["keyword"] = keyword_map.snomed_descriptor.apply(lambda x: re.sub(r'[^\w ]+', '', x))

        keyword_map["keyword"] = keyword_map["keyword"].str.lower().str.split()

        keyword_mappings = keyword_map.loc[:, ["pk", "sk", "keyword"]].explode("keyword")

        keyword_mappings = keyword_mappings.reset_index(drop=True).drop_duplicates()

        return keyword_mappings

    def _generate_table_items(self, cpt_mappings, keyword_mappings):
        table_items = []

        self._generate_cpt_items(table_items, cpt_mappings)

        self._generate_keyword_items(table_items, keyword_mappings)

        return table_items

    @classmethod
    def _generate_cpt_items(cls, table_items, cpt_mappings):
        for index in range(len(cpt_mappings)):
            row = cpt_mappings.iloc[index]
            table_items.append(row.to_dict())

    # pylint: disable=invalid-name
    @classmethod
    def _generate_keyword_items(cls, table_items, keywords_mapping):
        table_items += [
            dict(pk=f"{row.pk}:{row.sk}", sk=f"KEYWORD:{row.keyword}")
            for index, row in keywords_mapping.iterrows() if row.sk.startswith("CPT:")
        ]
