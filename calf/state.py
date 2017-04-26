import hashlib
import json
import os

STATE_FILE = '/tmp/calf-state-{}.json'


def state_path(path):
    return STATE_FILE.format(
        hashlib.md5(path.encode()).hexdigest()
    )


def read_state(path):
    try:
        with open(state_path(path), 'r') as f:
            return json.loads(f.read())
    except IOError:
        stat = os.stat(path)
        return [stat.st_ino, stat.st_rdev, stat.st_dev, 0]


def write_state(path, state):
    with open(state_path(path), 'w') as f:
        f.write(json.dumps(state))
