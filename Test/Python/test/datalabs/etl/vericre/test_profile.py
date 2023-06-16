''' Source: datalabs.etl.dag.vericre.profile '''
import importlib
import os
import sys

import pytest


# pylint: disable=import-outside-toplevel, unused-import
def test_cpt_api_dag_imports():
    import datalabs.etl.dag.vericre.profile

    assert True


# pylint: disable=import-outside-toplevel, unused-import
def test_dl_3460_not_implemented_yet():
    os.environ["ENABLE_FEATURE_DL_3460"] = "True"

    with pytest.raises(ImportError):
        # import datalabs.etl.dag.vericre.profile
        importlib.reload(sys.modules["datalabs.etl.dag.vericre.profile"])


# pylint: disable=import-outside-toplevel, unused-import
def test_dl_3462_not_implemented_yet():
    os.environ["ENABLE_FEATURE_DL_3462"] = "True"

    with pytest.raises(ImportError):
        importlib.reload(sys.modules["datalabs.etl.dag.vericre.profile"])


# pylint: disable=import-outside-toplevel, unused-import
def test_dl_3463_not_implemented_yet():
    os.environ["ENABLE_FEATURE_DL_3463"] = "True"

    with pytest.raises(ImportError):
        importlib.reload(sys.modules["datalabs.etl.dag.vericre.profile"])
