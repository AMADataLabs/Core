from   datetime import datetime, timedelta

import daemon


class SyncLooper(Thread):
    def __init__(self, event):
        Thread.__init__(self)
        self.stopped = event

    def run(self):
        duration = 0

        while not self.stopped.wait(duration):
            sync()

            duration = self.calculate_next_run_duration()

    @classmethod
    def sync(cls):
        pass

    @classmethod
    def calculate_next_run_duration(cls):
        return 15


def main():
    with daemon.DaemonContext():
        sync_looper = SyncLooper()

        sync_looper.run()
