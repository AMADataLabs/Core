import os

import repo
import datalabs.somepackage as app
# or from datalabs.somepackage import Application


if __name__ == '__main__':
    repo.configure()  # Setup the repo's PYTHONPATH

    # TODO: replace with some configuration management mechanism based on .env files
    os.environ['APP_CONFIG_VALUE_1'] = 'Value 1'
    os.environ['APP_CONFIG_VALUE_2'] = True

    app.main()
    # or Application().run()
