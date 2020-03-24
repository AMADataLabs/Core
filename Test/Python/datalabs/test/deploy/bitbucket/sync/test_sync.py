import dotenv
import logging
import os
import pathlib
import pytest
import tempfile

import datalabs.deploy.bitbucket.sync.sync as sync

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def test_bitbucket_synchronizer_runs_without_error(configuration, request_data):
    synchronizer = sync.BitBucketSynchronizer(configuration)

    synchronizer.sync(request_data)


@pytest.fixture
def configuration():
    return sync.Configuration(
        project='test-project',
        repository='test-repository',
        authorized_user='admin'
    )


@pytest.fixture
def request_data():
    return {
      "eventKey":"repo:refs_changed",
      "date":"2017-09-19T09:45:32+1000",
      "actor":{  
        "name":"admin",
        "emailAddress":"admin@example.com",
        "id":1,
        "displayName":"Administrator",
        "active":true,
        "slug":"admin",
        "type":"NORMAL"
      },
      "repository":{  
        "slug":"test-repository",
        "id":84,
        "name":"test-repository",
        "scmId":"git",
        "state":"AVAILABLE",
        "statusMessage":"Available",
        "forkable":true,
        "project":{  
          "key":"TESTPROJ",
          "id":84,
          "name":"test-project",
          "public":false,
          "type":"NORMAL"
        },
        "public":false
      },
      "changes":[  
        {  
          "ref":{  
            "id":"refs/heads/master",
            "displayId":"master",
            "type":"BRANCH"
          },
          "refId":"refs/heads/master",
          "fromHash":"ecddabb624f6f5ba43816f5926e580a5f680a932",
          "toHash":"178864a7d521b6f5e720b386b2c2b0ef8563e0dc",
          "type":"UPDATE"
        }
      ]
    }
