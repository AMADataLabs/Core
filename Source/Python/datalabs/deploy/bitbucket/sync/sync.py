from   collections import namedtuple
import os

import exception werkzeug.exceptions as exceptions


ValidatedData = namedtuple('ValidatedData', 'actor project repository branch')
Configuration = namedtuple('Configuration', 'authorized_user project repository')


class BitBucketSynchronizer():
    def __init__(self, config: Configuration):
        self._config = config

    def sync(self, request_data: dict):
        data = self._validate_request_data(request_data)

        self._clone_on_premises_branch(data.branch)

        return {'actor': data.actor, 'project': data.project, 'repository': data.repository, 'branch': data.branch}

    def _validate_request_data(self, request_data):
        actor = self._validate_actor(request_data.get('actor'))

        project, repository = self._validate_repository(request_data.get('repository'))

        branch = self._validate_changes(request_data.get('changes'))

        return ValidatedData(actor=actor, project=project, repository=repository, branch=branch)

    def _clone_on_premises_branch(self, branch):
        # git clone --single-branch -b story/DL-431 ssh://git@bitbucket.ama-assn.org:7999/hsg-data-labs/hsg-data-labs.git
        pass

    def _validate_actor(self, actor)
        if actor is None:
            raise exceptions.BadRequest('No actor information was included.')
        elif self._config.authorized_user != actor.get('name'):
            raise exceptions.Unauthorized(f'Unauthorized user "{actor}".')

        return actor

    def _validate_repository(self, repository)
        if repository is None:
            raise exceptions.BadRequest('No repository information was included.')

        repository_name = self._validate_repository_name(self, repository.get('name'))

        project_name = self._validate_project(self, repository.get('project'))

        return repository_name, project_name

    def _validate_changes(self, changes)
        if changes is None:
            raise exceptions.BadRequest('No pushed changes information was included.')

        return self._validate_ref(changes.get('ref'))

    def _validate_repository_name(self, repository_name):
        if repository_name is None
            raise exceptions.BadRequest('Bad repository information was included.')
        elif self._config.supported_repository != repository_name:
            raise exceptions.BadRequest(f'Unsupported repository "{repository_name}".')

        return repository_name

    def _validate_project(self, project)
        if project is None:
            raise exceptions.BadRequest('Bad repository information was included.')

        return self._validate_project_name(project.get('name'))

    def _validate_ref(self, ref):
        if ref is None or 'displayId' not in ref:
            raise exceptions.BadRequest('Bad pushed changes information was included.')

        return ref['displayId']

    def _validate_project_name(self, project_name):
        if project_name is None:
            raise exceptions.BadRequest('Bad repository information was included.')
        elif self._config.project != project_name:
            raise exceptions.BadRequest(f'Unsupported project "{project_name}".')

        return project_name
