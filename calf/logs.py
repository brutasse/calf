import os
import time

from .logging import log
from .state import read_state


def log_batches(path, watch_period=5):
    state = read_state(path)
    last_iter = None

    while True:
        if last_iter is not None:
            delay = (last_iter - time.time()) + watch_period
            if delay > 0:
                time.sleep(delay)
            else:
                log("last iteration was longer than period",
                    period=watch_period,
                    took=-1 * delay)
        last_iter = time.time()

        stat = os.stat(path)
        if [stat.st_ino, stat.st_rdev, stat.st_dev] != state[:3]:
            log("file changed, returning to beginning")
            state = [stat.st_ino, stat.st_rdev, stat.st_dev, 0]

        with open(path, 'r') as f:
            f.seek(state[-1])
            lines = f.readlines()
            pos = f.tell()
        state[-1] = pos
        yield state, lines
