from   datetime import datetime, timedelta
import os

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
            sync(dag_sync_config)

            duration = self.calculate_next_run_duration()

    @classmethod
    def sync(cls, config):
        synchronizer = dag.Synchronizer(config)

        synchronizer.start()

    @classmethod
    def calculate_next_run_duration(cls):
        return 15


def main():
    with daemon.DaemonContext():
        sync_looper = SyncLooper()

        sync_looper.run()
