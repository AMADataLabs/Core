""" source: datalabs.etl.cpt.knowledge_base.transform """
import json

import pandas
import pytest

from   datalabs.etl.cpt.knowledge_base.transform import KnowledgeBaseTransformerTask


# pylint: disable=redefined-outer-name, protected-access
def test_data_is_converted_properly_to_json(knowledge_base_data, knowledge_base):
    index_data = json.loads(KnowledgeBaseTransformerTask._convert_to_json(knowledge_base))

    assert len(index_data) == 2
    assert len(index_data[0]) == 7

    for index, datum  in enumerate(index_data):
        assert "article_id" in datum
        assert datum["document_id"] == knowledge_base_data["id"][index]
        assert datum["section"] == knowledge_base_data["section"][index]
        assert datum["subsection"] == knowledge_base_data["subsection"][index]
        assert datum["question"] == knowledge_base_data["question"][index]
        assert datum["answer"] == knowledge_base_data["answer"][index]
        assert datum["date"] == knowledge_base_data["date"][index]

@pytest.fixture
def knowledge_base_data():
    return dict(
        id=[42, 99],
        section=["Widgets", "Waggles"],
        subsection=["Floatsum", "Jetsum"],
        question=["How many woods would a woodchuck chuck", "Why"],
        answer=["A lot", "Because I said so"],
        date=["1985-10-12", "2251-12-06"]
    )


@pytest.fixture
def knowledge_base(knowledge_base_data):
    return pandas.DataFrame(data=knowledge_base_data)
