""" Apply the POLO address fitness model to the PPD. """
import settings  # pylint: disable=unused-import
import datalabs.analysis.polo.app as POLOFitnessScoringApp

if __name__ == '__main__':
    POLOFitnessScoringApp().run()
