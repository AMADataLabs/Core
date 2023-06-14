''' Source: datalabs.etl.dag.vericre.profile '''
import os
import pytest

# pylint: disable=import-outside-toplevel, unused-import
def test_cpt_api_dag_imports():
    import datalabs.etl.dag.vericre.profile

    assert True

# pylint: disable=no-name-in-module
def test_cpt_api_dag_imports_with_exception():
    os.environ["DL_3436"] = "True"

    with pytest.raises(ImportError):
        from datalabs.etl.vericre.profile.transform import AMAProfilesTransformerTask
        from datalabs.etl.vericre.profile.transform import VeriCreProfileSynchronizerTask
