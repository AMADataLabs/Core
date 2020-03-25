from   collections import namedtuple
import logging
import os
from   pathlib import Path
import subprocess
import tempfile
from   urllib.parse import urlparse

import werkzeug.exceptions as exceptions

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


ValidatedData = namedtuple('ValidatedData', 'actor project repository branch action')
Configuration = namedtuple('Configuration', 'url_on_prem url_cloud')


class BitBucketSynchronizer():
    def __init__(self, config: Configuration):
        self._config = config
        url = urlparse(self._config.url_on_prem)
        path = Path(url.path)

        self._repository_name = path.name.split('.')[0]
        self._project_name = path.parent.name

    def sync(self, request_data: dict):
        data = self._validate_request_data(request_data)
        LOGGER.info('Processing push to "%s" branch of repository "%s" under project "%s".', data.branch, data.repository, data.project)

        with tempfile.TemporaryDirectory() as temp_directory:
            os.chdir(temp_directory)

            LOGGER.info('-- Cloning --')
            self._clone_on_premises_branch(data.branch, data.action)

            os.chdir(Path(temp_directory).joinpath(data.repository))

            self._add_cloud_remote()

            LOGGER.info('-- Syncing --')
            self._sync_branch_to_cloud(data.branch, data.action)

        LOGGER.info('Done syncing "%s" branch of repository "%s" under project "%s".', data.branch, data.repository, data.project)

        return {'actor': data.actor, 'project': data.project, 'repository': data.repository, 'branch': data.branch, 'action': data.action}

    def _validate_request_data(self, request_data):
        actor = self._validate_actor(request_data.get('actor'))

        project, repository = self._validate_repository(request_data.get('repository'))

        branch, action = self._validate_changes(request_data.get('changes'))

        return ValidatedData(actor=actor, project=project, repository=repository, branch=branch, action=action)

    def _clone_on_premises_branch(self, branch, action):
        command = f'git clone --single-branch -b {"master" if action == "DELETE" else branch} {self._config.url_on_prem}'

        subprocess.call(command.split(' '))

    def _add_cloud_remote(self):
        command = f'git remote add cloud {self._config.url_cloud}'

        subprocess.call(command.split(' '))

    def _sync_branch_to_cloud(self, branch, action):
        if action == 'UPDATE':
            self._push_branch_to_cloud(branch)
        elif action == 'DELETE':
            self._push_branch_to_cloud(branch, delete=True)
        else:
            raise ValueError(f'Unexpected change action {action}.')

    def _push_branch_to_cloud(self, branch, delete=False):
        command = f'git push cloud --force {"--delete " if delete else ""}{branch}'

        subprocess.call(command.split(' '))

    def _validate_actor(self, actor):
        if actor is None:
            raise exceptions.BadRequest('No actor information.')
        elif 'name' not in actor:
            raise exceptions.BadRequest('Bad actor information.')

        return actor['name']

    def _validate_repository(self, repository):
        if repository is None:
            raise exceptions.BadRequest('No repository information.')

        repository_name = self._validate_repository_name(repository.get('slug'))

        project_name = self._validate_project(repository.get('project'))

        return repository_name, project_name

    def _validate_changes(self, changes):
        if not changes:
            raise exceptions.BadRequest('No pushed changes information.')

        branch = self._validate_ref(changes[0].get('ref'))

        action = self._validate_type(changes[0].get('type'))

        return branch, action

    def _validate_repository_name(self, repository_name):
        if repository_name is None:
            raise exceptions.BadRequest('Bad repository information.')
        elif self._repository_name != repository_name:
            raise exceptions.BadRequest(f'Unsupported repository "{repository_name}".')

        return repository_name

    def _validate_project(self, project):
        if project is None:
            raise exceptions.BadRequest('Bad repository information.')

        return self._validate_project_name(project.get('key').lower())

    def _validate_ref(self, ref):
        if ref is None or 'displayId' not in ref:
            raise exceptions.BadRequest('Bad pushed changes information.')

        return ref['displayId']

    def _validate_type(self, change_type):
        if change_type is None or change_type not in ['UPDATE', 'DELETE']:
            raise exceptions.BadRequest('Bad pushed changes information.')

        return change_type

    def _validate_project_name(self, project_name):
        if project_name is None:
            raise exceptions.BadRequest('Bad repository information.')
        elif self._project_name != project_name:
            raise exceptions.BadRequest(f'Unsupported project "{project_name}".')

        return project_name
