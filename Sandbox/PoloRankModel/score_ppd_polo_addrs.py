""" Apply the POLO address fitness model to the PPD. """
import settings  # pylint: disable=unused-import
from   datalabs.analysis.polo.app import POLOFitnessScoringApp

if __name__ == '__main__':
    POLOFitnessScoringApp().run()
