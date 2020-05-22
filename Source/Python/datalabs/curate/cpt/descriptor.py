"""Clinical Descriptor Table module"""
import pandas
import io


class ClinicianDescriptorParser:
    def parse(self, text: str) -> pandas.DataFrame:
        # clinicianDescriptor_file = cliniciandescriptor_obj['Body'].read()
        # stream = io.BytesIO(clinicianDescriptor_file)

        return pandas.read_csv(
            io.StringIO(text),
            names=['concept_id', 'cpt_code', 'clinician_descriptor_id', 'clinician_descriptor'],
            sep='\t',
            header=0,
            dtype=str
        )


class ConsumerDescriptorParser:
    def parse(self, text: str) -> pandas.DataFrame:
        # clinicianDescriptor_file = cliniciandescriptor_obj['Body'].read()
        # stream = io.BytesIO(clinicianDescriptor_file)

        return pandas.read_csv(
            io.StringIO(text),
            names=['concept_id', 'cpt_code', 'consumer_descriptor'],
            sep='\t',
            header=0,
            dtype=str
        )
