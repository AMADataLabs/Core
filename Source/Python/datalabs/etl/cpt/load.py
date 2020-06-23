""" CPT ETL Loader classes """
from   collections import defaultdict
from   dataclasses import dataclass
from   datetime import datetime
from   functools import reduce
import logging

import pandas
import sqlalchemy as sa

from   datalabs.access.orm import Database
from   datalabs.etl.load import Loader
import datalabs.etl.cpt.dbmodel as dbmodel
import datalabs.etl.cpt.transform as transform
import datalabs.feature as feature

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@dataclass
class IDs:
    old: list
    new: list


class TableUpdater:
    def __init__(self, session, model_class: type, primary_key, match_column: str):
        self._session = session
        self._model_class = model_class
        self._primary_key = primary_key
        self._match_column = match_column

        mapper = sa.inspect(self._model_class)
        self._columns = [column.key for column in mapper.attrs]

    def update(self, data):
        LOGGER.info('Updating table %s...', model.Release.__table__.name)
        current_models, current_data = self._get_current_data()

        old_data, new_data = self._differentiate_data(current_data, data)

        self._update_data(current_models, old_data)

        self._add_data(new_data)

    def _get_current_data(self):
        results = self._session.query(self._model_class).all()

        return results, self._get_query_results_data(results)

    def _differentiate_data(self, current_data, data):
        if 'modified_date' in current_data:
            current_data.drop('modified_date', axis=1)
        merged_data = pandas.merge(current_data, data, on=self._match_column, how='outer', suffixes=['_CURRENT', ''])

        if self._primary_key != self._match_column:
            merged_data[self._primary_key] = merged_data[self._primary_key + '_CURRENT']

        old_data = merged_data[~merged_data.isnull().any(axis=1)]

        new_data = merged_data[merged_data.isnull().any(axis=1)]

        return old_data, new_data

    def _update_data(self, models, data):
        LOGGER.info('    Updating existing rows...')
        filtered_data = self._filter_out_unchanged_data(data)

        filtered_models = self._get_matching_models(models, filtered_data)

        self._update_models(filtered_models, filtered_data)

    def _add_data(self, data):
        LOGGER.info('    Adding new rows...')
        models = self._create_models(data)

        self._add_models(models)

    def _get_query_results_data(self, results):
        return pandas.DataFrame({column:[getattr(result, column) for result in results] for column in self._columns})

    def _filter_out_unchanged_data(self, data):
        columns = self._get_changeable_columns()
        conditions = [getattr(data, column) != getattr(data, column + '_CURRENT') for column in columns]

        return data[reduce(lambda x, y: x | y, conditions)]

    def _get_matching_models(self, models, filtered_data):
        model_map = {getattr(model, self._primary_key):model for model in models}

        return [model_map[key] for key in getattr(filtered_data, self._primary_key)]

    def _update_models(self, models, data):
        columns = self._get_changeable_columns()

        for model, row in zip(models, data.itertuples()):
            self._update_model(model, row, columns)

    def _create_models(self, data):
        return [self._create_model(row) for row in data.itertuples(index=False)]

    def _add_models(self, models):
        for model in models:
            self._session.add(model)

    def _get_changeable_columns(self):
        columns = self._get_model_columns()

        columns.remove(self._primary_key)
        if self._match_column in columns:
            columns.remove(self._match_column)

        return columns

    @classmethod
    def _update_model(cls, model, row, columns):
        for column in columns:
            setattr(model, column, getattr(row, column))

        if hasattr(model, 'modified_date'):
            model.modified_date = datetime.utcnow().date()

    def _create_model(self, row):
        columns = self._get_model_columns()
        parameters = {column:getattr(row, column) for column in columns}
        model = self._model_class(**parameters)

        if hasattr(model, 'modified_date'):
            model.modified_date = datetime.utcnow().date()

        return model

    def _get_model_columns(self):
        mapper = sa.inspect(self._model_class)
        columns = [column.key for column in mapper.attrs]

        if 'modified_date' in columns:
            columns.remove('modified_date')

        return columns


class CPTRelationalTableLoader(Loader):
    def __init__(self, configuration):
        super().__init__(configuration)
        self._release = None
        self._codes = None
        self._pla_codes = None

    def load(self, data: transform.OutputData):
        with Database(key=self._configuration['DATABASE']) as database:
            self._session = database.session

            self._update_tables(data)

    def _update_tables(self, data: transform.OutputData):
        TableUpdater(self._session, dbmodel.Code, 'code', 'code').update(data.code)
        # self._release = self._update_release_table(data.release)

        # self._codes = self._update_codes_table(data.code)

        # self._update_release_code_mappings()

        # self._update_short_descriptors_table(data.short_descriptor)

        # self._update_medium_descriptors_table(data.medium_descriptor)

        # self._update_long_descriptors_table(data.long_descriptor)

        # self._update_modifier_types_table(data.modifier_type)

        # self._update_modifiers_table(data.modifier)

        # self._update_consumer_descriptors_table(data.consumer_descriptor)

        # self._update_clinician_descriptors_table(data.clinician_descriptor)

        # self._update_clinician_descriptor_code_mappings_table(data.clinician_descriptor_code_mapping)

        # if feature.enabled('PLA'):
        #     self._pla_codes = self._update_pla_code_table(data.pla_code)

        #     self._update_release_pla_code_mappings()

        #     self._update_pla_short_descriptor_table(data.pla_short_descriptor)

        #     self._update_pla_medium_descriptor_table(data.pla_medium_descriptor)

        #     self._update_pla_long_descriptor_table(data.pla_long_descriptor)

        #     self._update_manufacturer_table(data.pla_manufacturer)

        #     self._update_manufacturer_code_mapping_table(data.pla_manufacturer_code_mapping)

        #     self.__update_lab_table(data.pla_lab)

        #     self._update_lab_code_mapping_table(data.pla_lab_code_mapping)

        #     self._update_pla_release_code_mapping_table(data.pla_release_code_mapping)

    def _update_release_table(self, release_data):
        LOGGER.info('Processing releases...')
        release = model.Release(
            type=release_data.type.iloc[0],
            publish_date=release_data.publish_date.iloc[0],
            effective_date=release_data.effective_date.iloc[0]
        )
        conditions = [
            model.Release.type == release.type,
            model.Release.publish_date == release.publish_date,
            model.Release.effective_date == release.effective_date,
        ]
        matching_releases = self._session.query(model.Release).filter(*conditions).all()

        if len(matching_releases) == 0:
            LOGGER.info('    Adding new release...')
            self._session.add(release)
        else:
            LOGGER.info('    Using existing release...')

        return release

    def _update_codes_table(self, codes):
        LOGGER.info('Processing CPT codes...')
        current_codes = self._get_codes()
        old_codes = [code for code in codes.code if code in current_codes]
        new_codes = [code for code in codes.code if code not in current_codes]

        LOGGER.info('    Adding new codes...')
        for code in new_codes:
            self._session.add(model.Code(code=code))

        self._session.commit()

        return IDs(old_codes, new_codes)

    def _update_release_code_mappings(self):
        pass

    def _update_short_descriptors_table(self, descriptors):
        LOGGER.info('Processing short descriptors...')
        self._update_descriptors_table(model.ShortDescriptor, descriptors)

        self._session.commit()

    def _update_medium_descriptors_table(self, descriptors):
        LOGGER.info('Processing medium descriptors...')
        self._update_descriptors_table(model.MediumDescriptor, descriptors)

        self._session.commit()

    def _update_long_descriptors_table(self, descriptors):
        LOGGER.info('Processing long descriptors...')
        self._update_descriptors_table(model.LongDescriptor, descriptors)

        self._session.commit()

    def _update_modifier_types_table(self, modifier_types):
        LOGGER.info('Processing modifier types...')
        current_modifier_types = self._get_modifier_types()

        LOGGER.info('    Adding new modifier types...')
        for modifier_type in modifier_types.name:
            if modifier_type not in current_modifier_types:
                self._session.add(
                    model.ModifierType(name=modifier_type)
                )

        self._session.commit()

    def _update_modifiers_table(self, modifiers):
        LOGGER.info('Processing modifiers...')
        current_modifier_types = self._get_modifier_types()
        current_modifiers = self._get_modifiers()

        self._update_modifiers(modifiers, current_modifiers)

        self._add_modifiers(modifiers, current_modifiers, current_modifier_types)

        self._session.commit()

    def _update_consumer_descriptors_table(self, descriptors):
        LOGGER.info('Processing consumer descriptors...')
        self._update_descriptors_table(model.ConsumerDescriptor, descriptors)

        self._session.commit()

    def _update_clinician_descriptors_table(self, descriptors):
        LOGGER.info('Processing clinician descriptors...')
        current_descriptors = self._get_clinician_descriptors()
        new_descriptors = {
            id: descriptors[descriptors.id == id]
            for id in descriptors.id
            if id not in current_descriptors
        }

        missing_ids = self._update_descriptors(
            model.ClinicianDescriptor, 'id', current_descriptors.keys(), descriptors, current_descriptors
        )

        self._add_clinician_descriptors(list(new_descriptors.keys()) + missing_ids, descriptors)

        self._session.commit()

    def _update_clinician_descriptor_code_mappings_table(self, mappings):
        LOGGER.info('Processing clinician descriptor code mappings...')
        current_codes = self._get_codes()
        current_mappings = self._get_clinician_descriptor_code_mappings()
        new_mappings = {
            id: mappings.code[mappings.clinician_descriptor == id].iloc[0]
            for id in mappings.clinician_descriptor
            if id not in current_mappings
        }

        self._add_clinician_descriptor_code_mappings(new_mappings, current_codes)

        self._session.commit()

    def _update_pla_code_table(self, pla_codes):
        LOGGER.info('Processing PLA codes...')
        current_codes = self._get_pla_codes()
        old_codes = [code for code in pla_codes.code if code in current_codes]
        new_codes = [code for code in pla_codes.code if code not in current_codes]

        LOGGER.info('    Adding new codes...')
        for code in new_codes:
            self._session.add(model.PLACode(code=code))

        self._session.commit()

        return IDs(old_codes, new_codes)

    def _update_release_pla_code_mappings(self):
        pass

    def _get_codes(self):
        query = self._session.query(model.Code)

        return {row.code: row for row in query.all()}

    def _update_descriptors_table(self, model_class, descriptors):
        LOGGER.info('    Fetching current descriptors...')
        self._codes.new = self._codes.new.copy()
        current_descriptors = self._get_descriptors(model_class)

        missing_codes = self._update_descriptors(model_class, 'code', self._codes.old, descriptors, current_descriptors)

        self._add_descriptors(model_class, self._codes.new + missing_codes, descriptors)

    def _get_modifier_types(self):
        query = self._session.query(model.ModifierType)

        return {row.name: row for row in query.all()}

    def _get_modifiers(self):
        query = self._session.query(model.Modifier)

        return {row.modifier: row for row in query.all()}

    @classmethod
    def _update_modifiers(cls, modifiers, current_modifiers):
        LOGGER.info('    Updating old modifiers...')
        old_modifiers = [modifier for modifier in modifiers.modifier if modifier in current_modifiers]

        for modifier in old_modifiers:
            if modifier not in current_modifiers:
                missing_modifiers.append(modifier)
            else:
                cls._update_descriptor('modifier', modifier, modifiers, current_modifiers)

    def _add_modifiers(self, modifiers, current_modifiers, modifier_types):
        LOGGER.info('    Adding new modifiers...')
        new_modifiers = [modifier for modifier in modifiers.modifier if modifier not in current_modifiers]
        LOGGER.debug('New Modifiers: %s', new_modifiers)

        for modifier in new_modifiers:
            modifier_details = modifiers[modifiers.modifier == modifier].iloc[0]
            modifier_type = modifier_types[modifier_details.type]
            descriptor = modifier_details.descriptor

            self._session.add(model.Modifier(modifier=modifier, type=modifier_type.id, descriptor=descriptor))

    def _get_clinician_descriptors(self):
        query = self._session.query(model.ClinicianDescriptor)

        return {row.id: row for row in query.all()}

    def _get_clinician_descriptor_code_mappings(self):
        query = self._session.query(model.ClinicianDescriptorCodeMapping)

        return {row.clinician_descriptor: row for row in query.all()}

    def _add_clinician_descriptors(self, new_ids, descriptors):
        LOGGER.info('    Adding new descriptors...')
        for id in new_ids:
            matches = descriptors[descriptors.id == id]

            if len(matches) == 0:
                LOGGER.warn('No %s for code "%s".', model.ClinicianDescriptor.__name__, id)
                continue
            else:
                LOGGER.debug('Adding Clinician Descriptor with id %s', id)

            self._session.add(model.ClinicianDescriptor(id=id, descriptor=matches.descriptor.iloc[0]))

    def _add_clinician_descriptor_code_mappings(self, mappings, codes):
        LOGGER.info('    Adding new mappings...')
        for id, code in mappings.items():
            if code not in codes:
                LOGGER.warn('Ignoring mapping of Clinician Descriptor %s to non-existant CPT code %s', id, code)
                continue
            else:
                LOGGER.debug('Mapping Clinician Descriptor with id %s to CPT code %s', id, code)

            self._session.add(model.ClinicianDescriptorCodeMapping(clinician_descriptor=id, code=code))

    def _get_descriptors(self, model_class):
        query = self._session.query(model_class)

        return {row.code: row for row in query.all()}

    @classmethod
    def _update_descriptors(cls, model_class, primary_key_name, old_primary_keys, descriptors, current_descriptors):
        LOGGER.info('    Updating old descriptors...')
        missing_primary_keys = []

        for primary_key in old_primary_keys:
            if primary_key not in current_descriptors:
                missing_primary_keys.append(primary_key)
            else:
                cls._update_descriptor(primary_key_name, primary_key, descriptors, current_descriptors)

        return missing_primary_keys

    def _add_descriptors(self, model_class, new_codes, descriptors):
        LOGGER.info('    Adding new descriptors...')
        for code in new_codes:
            matches = descriptors.descriptor[descriptors.code == code]

            if len(matches) == 0:
                LOGGER.warn('No %s for code "%s".', model_class.__name__, code)
                continue

            descriptor = matches.iloc[0]

            self._session.add(model_class(code=code, descriptor=descriptor))

    @classmethod
    def _update_descriptor(cls, primary_key_name, primary_key, descriptors, current_descriptors):
        descriptor = descriptors.descriptor[descriptors[primary_key_name] == primary_key].iloc[0]

        if current_descriptors[primary_key] != descriptor:
            current_descriptors[primary_key].descriptor = descriptor

    def _get_pla_codes(self):
        query = self._session.query(model.PLACode)

        return {row.code: row for row in query.all()}

    def _update_pla_short_descriptor_table(self, codes, descriptors):
        LOGGER.info('Processing short pla descriptors...')
        self._update_pla_descriptors_table(model.PLAShortDescriptor, codes, descriptors)

        self._session.commit()

    def _update_pla_medium_descriptor_table(self, codes, descriptors):
        LOGGER.info('Processing medium descriptors...')
        self._update_pla_descriptors_table(model.PLAMediumDescriptor, codes, descriptors)

        self._session.commit()

    def _update_pla_long_descriptor_table(self, codes, descriptors):
        LOGGER.info('Processing long descriptors...')
        self._update_pla_descriptors_table(model.PLALongDescriptor, codes, descriptors)

        self._session.commit()

    def _update_pla_descriptors_table(self, model_class, codes, descriptors):
        LOGGER.info('    Fetching current descriptors...')
        self._codes.new = self._codes.new.copy()
        current_descriptors = self._get_pla_descriptors(model_class)

        missing_codes = self._update_pla_descriptors('code', self._codes.old, descriptors, current_descriptors)

        self._add_pla_descriptors(model_class, self._codes.new + missing_codes, descriptors)

    @classmethod
    def _update_pla_descriptors(cls, primary_key_name, old_primary_keys, descriptors, current_descriptors):
        LOGGER.info('    Updating old descriptors...')
        missing_primary_keys = []

        for primary_key in old_primary_keys:
            if primary_key not in current_descriptors:
                missing_primary_keys.append(primary_key)
            else:
                cls._update_pla_descriptor(primary_key_name, primary_key, descriptors, current_descriptors)

        return missing_primary_keys

    def _add_pla_descriptors(self, model_class, new_codes, descriptors):
        LOGGER.info('    Adding new descriptors...')
        for code in new_codes:
            matches = descriptors.descriptor[descriptors.code == code]

            if len(matches) == 0:
                LOGGER.warn('No %s for code "%s".', model_class.__name__, code)
                continue

            descriptor = matches.iloc[0]

            self._session.add(model_class(code=code, descriptor=descriptor))

    @classmethod
    def _update_pla_descriptor(cls, primary_key_name, primary_key, descriptors, current_descriptors):
        descriptor = descriptors.descriptor[descriptors[primary_key_name] == primary_key].iloc[0]

        if current_descriptors[primary_key] != descriptor:
            current_descriptors[primary_key].descriptor = descriptor

    def _get_pla_descriptors(self, model_class):
        query = self._session.query(model_class)

        return {row.code: row for row in query.all()}

    def _update_manufacturer_table(self, manufacturer):
        LOGGER.info('Processing manufacturers...')
        current_manufacturer = self._get_manufacturer()

        new_manufacturer = {
            id: manufacturer[manufacturer.id == id]
            for id in manufacturer.id
            if id not in current_manufacturer
        }

        missing_ids = self._update_pla_descriptors(
            'id', current_manufacturer.keys(), manufacturer, current_manufacturer
        )

        self._add_manufacturer(list(new_manufacturer.keys()) + missing_ids, manufacturer)

        self._session.commit()

    def _get_manufacturer(self):
        query = self._session.query(model.Manufacturer)

        return {row.id: row for row in query.all()}

    def _add_manufacturer(self, new_ids, manufacturer):
        LOGGER.info('    Adding new manufacturers...')
        for id in new_ids:
            matches = manufacturer[manufacturer.id == id]

            if len(matches) == 0:
                LOGGER.warn('No %s for id "%s".', model.Manufacturer.__name__, id)
                continue
            else:
                LOGGER.debug('Adding Manufacturer with id %s', id)

            self._session.add(model.Manufacturer(id=id, name=matches.manufacturer.iloc[0]))

    def _update_manufacturer_code_mapping_table(self, mappings):
        LOGGER.info('Processing manufacturer code mappings...')
        current_codes = self._get_pla_codes()
        current_mappings = self._get_manufacturer_code_mapping()
        new_mappings = {
            id: mappings.code[mappings.manufacturer == id].iloc[0]
            for id in mappings.manufacturer
            if id not in current_mappings
        }

        self._add_manufacturer_code_mappings(new_mappings, current_codes)

        self._session.commit()

    def _get_manufacturer_code_mapping(self):
        query = self._session.query(model.ManufacturerPLACodeMapping)

        return {row.manufacturer: row for row in query.all()}

    def _add_manufacturer_code_mappings(self, mappings, codes):
        LOGGER.info('    Adding new mappings...')
        for id, code in mappings.items():
            if code not in codes:
                LOGGER.warn('Ignoring mapping of Manufacturer %s to non-existant PLA code %s', id, code)
                continue
            else:
                LOGGER.debug('Mapping Manufacturer with id %s to PLA code %s', id, code)

            self._session.add(model.ManufacturerPLACodeMapping(manufacturer=id, code=code))

    def __update_lab_table(self, lab):
        LOGGER.info('Processing lab names...')
        current_lab = self._get_lab()

        new_lab = {
            id: lab[lab.id == id]
            for id in lab.id
            if id not in current_lab
        }

        missing_ids = self._update_pla_descriptors(
            'id', current_lab.keys(), lab, current_lab
        )

        self._add_lab(list(new_lab.keys()) + missing_ids, lab)

        self._session.commit()

    def _get_lab(self):
        query = self._session.query(model.Lab)

        return {row.id: row for row in query.all()}

    def _add_lab(self, new_ids, lab):
        LOGGER.info('    Adding new lab names...')
        for id in new_ids:
            matches = lab[lab.id == id]

            if len(matches) == 0:
                LOGGER.warn('No %s for id "%s".', model.Lab.__name__, id)
                continue
            else:
                LOGGER.debug('Adding Lab name with id %s', id)

            self._session.add(model.Lab(id=id, name=matches.manufacturer.iloc[0]))

    def _update_lab_code_mapping_table(self, mappings):
        LOGGER.info('Processing lab code mappings...')
        current_codes = self._get_pla_codes()
        current_mappings = self._get_lab_code_mapping()
        new_mappings = {
            id: mappings.code[mappings.lab == id].iloc[0]
            for id in mappings.lab
            if id not in current_mappings
        }

        self._add_lab_code_mappings(new_mappings, current_codes)

        self._session.commit()

    def _get_lab_code_mapping(self):
        query = self._session.query(model.LabPLACodeMapping)

        return {row.manufacturer: row for row in query.all()}

    def _add_lab_code_mappings(self, mappings, codes):
        LOGGER.info('    Adding new mappings...')

        for id, code in mappings.items():
            if code not in codes:
                LOGGER.warn('Ignoring mapping of Lab names %s to non-existant PLA code %s', id, code)
                continue
            else:
                LOGGER.debug('Mapping Lab names with id %s to PLA code %s', id, code)

            self._session.add(model.LabPLACodeMapping(lab=id, code=code))

