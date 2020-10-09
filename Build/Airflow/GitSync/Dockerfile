FROM k8s.gcr.io/git-sync:v3.1.2

ENV GIT_SYNC_REPO git@bitbucket.org:hsdatalabs/hsg-data-labs.git
ENV GIT_SYNC_BRANCH master
ENV GIT_SUBPATH Source/Python/datalabs/dag
ENV GIT_SYNC_SSH true
ENV GIT_SSH_KEY_FILE /tmp/id_rsa
ENV GIT_SSH_KNOWN_HOSTS_FILE /tmp/known_hosts
ENV GIT_SYNC_WAIT 30

USER root
COPY ./id_rsa /tmp/id_rsa
COPY ./known_hosts /tmp/known_hosts
RUN mkdir -p /tmp/git
RUN chown git-sync /tmp/*

USER git-sync
