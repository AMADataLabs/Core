import logging
import pandas
import json

from  dataclasses import dataclass
from datalabs.analysis.quality.transform import TransformerTask
from datalabs.parameter import add_schema


logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@add_schema
@dataclass
class PersonTransformerParameters:
    metadata: str = None



class PersonTransformerTask(TransformerTask):

    PARAMETER_CLASS = PersonTransformerParameters
    
    
    def _parse_metadata(self, metadata):
        
        json_metadata = json.loads(metadata)

        return {list(d[1].keys())[0]:{"index": d[0], "seperator": list(d[1].values())[0]} for d in enumerate(json_metadata)}

  
    def _preprocess(self, dataset):

        dataset = [self._to_lowercase(data) for data in dataset]
        
        return dataset
        
    @classmethod        
    def _to_lowercase(cls, data):
       data.rename(columns=lambda x: x.lower(), inplace=True)
       return data
        
    def _create_entity(self, dataset):
    
        race_ethnicity, medical_education_num, person_type, party_ids, entity_ids, person_details, person_name = dataset
        
        ids = pandas.merge(entity_ids, party_ids, on='party_id')
        person_data = pandas.merge(ids, medical_education_num, left_on='me', right_on='medical_education_number', how='right')
        person_data = pandas.merge(person_data, person_type, on='entity_id' ,how='left').drop_duplicates()
        person_data = pandas.merge(person_data, person_name, on='party_id',how='left').drop_duplicates()
        person_data = pandas.merge(person_data, race_ethnicity, on='medical_education_number', how='left')
        person_data = pandas.merge(person_data, person_details, on='party_id',how='left').drop_duplicates()
        
        return [person_data]


    def _postprocess(self, dataset):

        dataset[0].drop(columns=['me', 'med_edu_nbr'], inplace=True)
        
        return dataset



