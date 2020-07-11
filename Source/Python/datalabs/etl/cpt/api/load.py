""" CPT ETL Loader classes """
from   collections import defaultdict
from   dataclasses import dataclass
from   datetime import datetime
from   functools import reduce
import logging

import pandas
import sqlalchemy as sa

from   datalabs.access.orm import Database
from   datalabs.etl.database import DatabaseTaskMixin
from   datalabs.etl.load import LoaderTask
import datalabs.etl.cpt.dbmodel as dbmodel
import datalabs.etl.cpt.transform as transform
import datalabs.feature as feature

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@dataclass
class IDs:
    old: list
    new: list


class CPTRelationalTableLoaderTask(LoaderTask, DatabaseTaskMixin):
    def __init__(self, parameters):
        super().__init__(parameters)
        self._release = None
        self._codes = None
        self._pla_codes = None

    def load(self, data: transform.OutputData):
        with Database(key=self._parameters['DATABASE']) as database:
            self._session = database.session

            self._update_tables(data)

    def _update_tables(self, data: transform.OutputData):
        release_table_updater = ReleaseTableUpdater(self._session)
        release_table_updater.update(data.release)

        TableUpdater(self._session, dbmodel.Code, 'code').update(data.code)

        ReleaseCodeMappingTableUpdater(self._session, release_table_updater.release_id).update(
            data.release_code_mapping
        )

        TableUpdater(self._session, dbmodel.ShortDescriptor, 'code').update(data.short_descriptor)

        TableUpdater(self._session, dbmodel.MediumDescriptor, 'code').update(data.medium_descriptor)

        TableUpdater(self._session, dbmodel.LongDescriptor, 'code').update(data.long_descriptor)

        TableUpdater(self._session, dbmodel.ModifierType, 'id', match_column='name').update(data.modifier_type)

        ModifierTableUpdater(self._session).update(data.modifier)

        TableUpdater(self._session, dbmodel.ConsumerDescriptor, 'code').update(data.consumer_descriptor)

        TableUpdater(self._session, dbmodel.ClinicianDescriptor, 'id').update(data.clinician_descriptor)

        TableUpdater(self._session, dbmodel.ClinicianDescriptorCodeMapping, 'clinician_descriptor').update(
            data.clinician_descriptor_code_mapping
        )

        if feature.enabled('PLA'):
            TableUpdater(self._session, dbmodel.PLACode, 'code').update(data.pla_code)

            # TableUpdater(self._session, dbmodel.ReleasePLACodeMapping, 'release').update(???)

            TableUpdater(self._session, dbmodel.PLAShortDescriptor, 'code').update(data.pla_short_descriptor)

            TableUpdater(self._session, dbmodel.PLAMediumDescriptor, 'code').update(data.pla_medium_descriptor)

            TableUpdater(self._session, dbmodel.PLALongDescriptor, 'code').update(data.pla_long_descriptor)

            TableUpdater(self._session, dbmodel.Manufacturer, 'code').update(data.manufacturer)

            TableUpdater(self._session, dbmodel.ManufacturerPLACodeMapping, 'code').update(
                data.manufacturer_pla_code_mapping
            )

            TableUpdater(self._session, dbmodel.Lab, 'code').update(data.lab)

            TableUpdater(self._session, dbmodel.LabPLACodeMapping, 'code').update(data.lab_pla_code_mapping)

        self._session.commit()


class TableUpdater:
    def __init__(self, session, model_class: type, primary_key, match_column: str = None):
        self._session = session
        self._model_class = model_class
        self._primary_key = primary_key
        self._match_column = match_column or self._primary_key

        mapper = sa.inspect(self._model_class)
        self._columns = [column.key for column in mapper.attrs]

    def update(self, data):
        LOGGER.info('Updating table %s...', self._model_class.__table__.name)
        current_models, current_data = self._get_current_data()
        LOGGER.debug('New data: %s', data)

        old_data, new_data = self._differentiate_data(current_data, data)

        self._update_data(current_models, old_data)

        self._add_data(new_data)

    def _get_current_data(self):
        results = self._session.query(self._model_class).all()

        return results, self._get_query_results_data(results)

    def _differentiate_data(self, current_data, data):
        merged_data = self._merge_data(current_data, data)

        old_data = merged_data[~merged_data.isnull().any(axis=1)]

        new_data = merged_data[merged_data.isnull().any(axis=1)]
        new_data = self._remove_missing_rows(new_data)

        return old_data, new_data

    def _update_data(self, models, data):
        filtered_data = self._filter_out_unchanged_data(data)

        filtered_models = self._get_matching_models(models, filtered_data)

        self._update_models(filtered_models, filtered_data)

    def _add_data(self, data):
        models = self._create_models(data)

        self._add_models(models)

    def _get_query_results_data(self, results):
        return pandas.DataFrame({column:[getattr(result, column) for result in results] for column in self._columns})

    def _merge_data(self, current_data, data):
        current_data = self._remove_modified_date(current_data)  # set programmatically

        merged_data = pandas.merge(current_data, data, on=self._match_column, how='outer', suffixes=['_CURRENT', ''])

        merged_data = self._delete_if_missing(merged_data)
        LOGGER.debug('Merged data: %s', merged_data)

        return self._sync_primary_key(merged_data)

    def _remove_missing_rows(self, data):
        current_columns = [column.name + '_CURRENT' for column in self._model_class.__table__.columns]
        drop_columns = [column for column in current_columns if column in data]
        reduced_data = data.drop(drop_columns, axis=1)
        reduced_data = reduced_data.drop(self._primary_key, axis=1)
        delete_indices = reduced_data.isnull().any(axis=1)

        return data.drop(data.index[delete_indices])

    @classmethod
    def _remove_modified_date(cls, data):
        if 'modified_date' in data:
            data.drop('modified_date', axis=1)

        return data

    @classmethod
    def _delete_if_missing(cls, data):
        if 'deleted' in data:
            data.loc[data.deleted.isnull(), 'deleted'] = True

        return data

    def _sync_primary_key(self, data):
        current_primary_key = self._primary_key + '_CURRENT'
        if current_primary_key in data and self._primary_key != self._match_column:
            data[self._primary_key] = data[current_primary_key]

        return data

    def _filter_out_unchanged_data(self, data):
        columns = self._get_changeable_columns()
        conditions = [getattr(data, column) != getattr(data, column + '_CURRENT') for column in columns]
        filtered_data = data

        if conditions:
            filtered_data = data[reduce(lambda x, y: x | y, conditions)]
        else:
            filtered_data = pandas.DataFrame(columns=data.columns.values)

        return filtered_data

    def _get_matching_models(self, models, filtered_data):
        model_map = {getattr(model, self._primary_key):model for model in models}

        return [model_map[key] for key in getattr(filtered_data, self._primary_key)]

    def _update_models(self, models, data):
        LOGGER.info('    Updating %d existing rows...', len(models))
        columns = self._get_changeable_columns()

        for model, row in zip(models, data.itertuples()):
            self._update_model(model, row, columns)

    def _create_models(self, data):
        return [self._create_model(row) for row in data.itertuples(index=False)]

    def _add_models(self, models):
        LOGGER.info('    Adding %d new rows...', len(models))
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
        primary_key = getattr(row, self._primary_key)

        if primary_key != primary_key:
            setattr(model, self._primary_key, None)

        if hasattr(model, 'modified_date'):
            model.modified_date = datetime.utcnow().date()

        return model

    def _get_model_columns(self):
        mapper = sa.inspect(self._model_class)
        columns = [column.key for column in mapper.attrs]

        if 'modified_date' in columns:
            columns.remove('modified_date')

        return columns


class ReleaseTableUpdater(TableUpdater):
    def __init__(self, session):
        super().__init__(session, dbmodel.Release, 'id', match_column='publish_date')

        self._current_models = None
        self._new_models = None
        self._release_id = None

    @property
    def release_id(self):
        return self._release_id
    

    def update(self, data):
        super().update(data)

        self._session.commit()

        if self._new_models:
            self._release_id = self._new_models[-1].id
        else:
            self._release_id = self._current_models[-1].id

    def _get_current_data(self):
        self._current_models, current_data = super()._get_current_data()

        self._current_models.sort(key=lambda x: x.publish_date)

        return self._current_models, current_data

    def _add_data(self, data):
        self._new_models = self._create_models(data)

        self._add_models(self._new_models)

    @classmethod
    def _delete_if_missing(cls, data):
        return data


class ReleaseCodeMappingTableUpdater(TableUpdater):
    def __init__(self, session, release_id: int):
        super().__init__(session, dbmodel.ReleaseCodeMapping, 'id')

        self._release_id = release_id

    def _differentiate_data(self, current_data, data):
        current_columns = [column+'_CURRENT' for column in self._get_changeable_columns()]
        old_data = pandas.DataFrame(columns=data.columns.values.tolist()+current_columns)
        new_data = data
        new_data.release = self._release_id

        if all(current_data.release == self._release_id):
            new_data = pandas.DataFrame(columns=new_data.columns)

        return old_data, new_data


class ModifierTableUpdater(TableUpdater):
    def __init__(self, session):
        super().__init__(session, dbmodel.Modifier, 'modifier')

        self._modifier_types = None

    def _get_current_data(self):
        self._modifier_types = {type_.name:type_.id for type_ in self._session.query(dbmodel.ModifierType).all()}

        return super()._get_current_data()

    def _merge_data(self, current_data, data):
        merged_data = super()._merge_data(current_data, data)

        merged_data.loc[:, 'type'] = merged_data.type.apply(lambda x: self._modifier_types[x])

        return merged_data
