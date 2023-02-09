""" License Movement PPMA update pipeline - Transformer """
from   dataclasses import dataclass
from   io import BytesIO
import pandas as pd

# pylint: disable=import-error,unused-import,unused-variable
from   datalabs.analysis.ppma.license_movement.finder import LicenseMovementFinder
from   datalabs.parameter import add_schema
from   datalabs.task import Task


@add_schema
@dataclass
class LicenseMovementTransformerParameter:
    execution_time: str = None


class LicenseMovementTransformerTask(Task):
    PARAMETER_CLASS = LicenseMovementTransformerParameter

    def run(self):
        mismatch_data, old_ppma_data, credentialing_data, ppd = [pd.read_csv(BytesIO(file)) for file in self._data]

        finder = LicenseMovementFinder()

        data = finder.find_potential_updates(data=mismatch_data, old_ppma_data=old_ppma_data)
        data = finder.filter_to_allowed_states(data=data)
        data = finder.filter_on_credentialing_zip_distance(data=data, credentialing_data=credentialing_data, ppd=ppd)
        data = finder.filter_to_valid_credentialing_data(data=data)

        batch_data = finder.format_batch_load_file(data=data)

        output = batch_data.to_csv(sep='|', index=False).encode()

        return [output]
