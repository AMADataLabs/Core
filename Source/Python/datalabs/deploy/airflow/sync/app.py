""" Airflow DAG sync application (main loop). """
import logging
import os
from   threading import Thread, Event

import datalabs.deploy.airflow.sync.dag as dag
from   datalabs.deploy.ssh.key import load_key_from_variable

logging.basicConfig(format='%(asctime)-15s %(levelname)s: %(message)s')
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class SyncLooper(Thread):
    def __init__(self, event):
        Thread.__init__(self)

        self.stopped = event

    def run(self):
        duration = 0
        dag_sync_config = dag.Configuration(
            os.getenv('CLONE_URL'),
            os.getenv('BRANCH'),
            os.getenv('DAG_SOURCE_PATH'),
            os.getenv('DAG_TARGET_PATH')
        )

        load_key_from_variable('GIT_SSH_KEY', '/Sync/id_rsa')

        while not self.stopped.wait(duration):
            try:
                self._sync(dag_sync_config)
            except Exception as e:
                LOGGER.exception(f"Failed to sync DAGs.")

            duration = self._calculate_next_run_duration()

    @classmethod
    def _sync(cls, config):
        synchronizer = dag.Synchronizer(config)

        synchronizer.sync()

    @classmethod
    def _calculate_next_run_duration(cls):
        return float(os.getenv('SYNC_INTERVAL'))


def main():
    stop_event = Event()
    sync_looper = SyncLooper(stop_event)

    sync_looper.start()

print(__name__)
if __name__ == "__main__":
    main()
