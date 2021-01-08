from   datetime import datetime, timedelta
import os
from   threading import Thread, Event

import daemon

import datalabs.deploy.airflow.sync.dag as dag


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

        while not self.stopped.wait(duration):
            self._sync(dag_sync_config)

            duration = self._calculate_next_run_duration()

    @classmethod
    def _sync(cls, config):
        synchronizer = dag.Synchronizer(config)

        synchronizer.sync()

    @classmethod
    def _calculate_next_run_duration(cls):
        return 15


def main():
    # with daemon.DaemonContext():
    stop_event = Event()
    sync_looper = SyncLooper(stop_event)

    sync_looper.start()

print(__name__)
if __name__ == "__main__":
    main()
