import os

def enabled(feature_name):
    feature_variable = os.environ.get('ENABLE_FEATURE_' + feature_name)
    feature_enabled = False

    if feature_variable is not None and feature_variable.upper() == 'TRUE':
        feature_enabled = True

    return feature_enabled