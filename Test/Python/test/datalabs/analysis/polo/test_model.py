""" source: datalabs.analysis.polo.model """
from   datetime import datetime
import os
import tempfile

import mock
import pandas
import pytest

import datalabs.analysis.polo.model as polo


# pylint: disable=redefined-outer-name,protected-access
def test_init_sets_properties(archive_dir):
    model = polo.POLOFitnessModel(archive_dir)

    assert model._archive_dir == archive_dir
    assert model.start_time is None
    assert model.ppd_datestamp is None


# pylint: disable=redefined-outer-name,protected-access
def test_init_creates_missing_archive_directory(archive_dir):
    archive_dir = archive_dir + os.sep + 'archive_dir'
    model = polo.POLOFitnessModel(archive_dir)

    assert os.path.exists(model._archive_dir)


# pylint: disable=redefined-outer-name,protected-access
def test_merge_ppd_and_aims_data_runs(model, data):
    with mock.patch('datalabs.analysis.polo.model.create_ppd_scoring_data') as create_ppd_scoring_data:
        create_ppd_scoring_data.return_value = data
        model._merge_ppd_and_aims_data(
            data,
            polo.EntityData(
                entity_comm_at=data,
                entity_comm_usg=data,
                post_addr_at=data,
                license_lt=data,
                entity_key_et=data
            )
        )


# pylint: disable=redefined-outer-name,protected-access
def test_curate_input_data_for_model_runs(model, data, variables):
    model._curate_input_data_for_model(data, variables)


# pylint: disable=redefined-outer-name,protected-access
def test_archive_model_input_data_produces_data_file(model, data):
    assert len(os.listdir(model._archive_dir)) == 0

    model._archive_model_input_data(data)

    assert len(os.listdir(model._archive_dir)) == 1


def test_score(model, data, variables):
    with mock.patch('datalabs.analysis.polo.model.get_class_predictions') as get_class_predictions:
        get_class_predictions.return_value = ([0], [0])
        model._score(None, variables, data, data)


@pytest.fixture
def archive_dir():
    with tempfile.TemporaryDirectory() as directory:
        yield directory


@pytest.fixture
def model(archive_dir):
    model = polo.POLOFitnessModel(archive_dir)
    model._start_time = datetime.now()
    model._ppd_datestamp = '20200101'

    return model


@pytest.fixture
def data():
    return pandas.DataFrame({
        'ppd_medschool_grad_year': [1994],
        'ppd_birth_year': [1974],
        'ent_comm_begin_dt': [datetime.now()],
        'ent_comm_end_dt': [datetime.now()],
        'lic_match': [0],
        'ppd_top_cd': [0],
        'ppd_prim_spec_cd': [0],
    })


@pytest.fixture
def variables(data):
    return polo.ModelVariables(
        input=[
            'ppd_medschool_grad_year',
            'ppd_birth_year',
            'ent_comm_begin_dt',
            'ent_comm_end_dt',
            'lic_match',
            'ppd_top_cd',
            'ppd_prim_spec_cd',
        ],
        feature=[
            'ppd_medschool_grad_year',
            'ppd_birth_year',
            'ent_comm_begin_dt',
            'ent_comm_end_dt',
            'lic_match',
            'ppd_top_cd_0',
            'ppd_prim_spec_cd',
        ],
        output=[
            'ppd_medschool_grad_year',
            'ppd_birth_year',
            'ent_comm_begin_dt',
            'ent_comm_end_dt',
            'lic_match',
            'ppd_top_cd',
            'ppd_prim_spec_cd',
        ],
    )
    return [
        'ppd_medschool_grad_year',
        'ppd_birth_year',
        'ent_comm_begin_dt',
        'ent_comm_end_dt',
        'lic_match',
        'ppd_top_cd_0',
        'ppd_prim_spec_cd',
    ]
