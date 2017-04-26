import socket
from datetime import date

from raven import Client as Raven

from . import es
from .logging import log
from .logs import log_batches
from .processors import load_processors
from .state import write_state


class Calf:
    def __init__(self, cluster, path, processors=None, sentry_dsn=None):
        self.cluster = cluster.strip('/')
        self.path = path
        if processors is None:
            processors = []
        self.processors = load_processors(processors)
        self.raven = None
        if sentry_dsn:
            self.raven = Raven(dsn=sentry_dsn)
        self._source_host = socket.gethostname()

        es.ensure_index_template(cluster)

    def run(self):
        try:
            for state, lines in log_batches(self.path):
                if not lines:
                    continue

                es.send_batch(self.cluster, filter(None,
                                                   map(self.process, lines)))

                if lines:
                    write_state(self.path, state)
        except Exception:
            if self.raven is not None:
                self.raven.captureException()
            raise

    def process(self, line):
        dt, message = line.split(' ', 1)
        prefix, message = message.split(':', 1)
        *hosts, program = prefix.split()
        host, *hosts = hosts

        day = date(*map(int, dt.split('T')[0].split('-')))

        pid = None
        if '[' in program:
            program, pid = program.strip(']').split('[', 1)

        event = {
            '_type': 'relp',
            '_index': day.strftime(es.INDEX_TEMPLATE),
            'type': 'relp',
            'message': message.strip(),
            'logsource': host,
            'program': program,
            'source_host': self._source_host,
            '@version': '1',
            '@timestamp': dt,
        }
        if pid is not None:
            event['pid'] = pid
        if hosts:
            if len(hosts) == 1:
                [event['logsource2']] = hosts
            else:
                event['logsources'] = hosts

        try:
            for processor in self.processors:
                event = processor(event, line)
                if event is None:
                    return
        except Exception as e:
            log("caught exception during processing:", exception=str(e),
                level='err')
            if self.raven is not None:
                self.raven.captureException()
        return event
