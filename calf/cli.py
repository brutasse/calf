import argparse

from .core import Calf
from .logging import levels, set_level
from .processors import library


def main():
    parser = argparse.ArgumentParser(
        description=(
            'Tail syslog, process messages and send them to Elasticsearch'))
    parser.add_argument('--path', dest='path', default='/var/log/syslog',
                        help='Path to the log file to tail')
    parser.add_argument('--cluster', dest='cluster',
                        default='http://localhost:9200',
                        help='Elasticsearch cluster address')
    parser.add_argument('--sentry-dsn', dest='sentry_dsn',
                        default=None, help='DSN for error reporting to Sentry')
    parser.add_argument('--processors', dest='processors', nargs='*',
                        help=('List of processors, either built-in or dotted '
                              'path to custom processors. Available built-in '
                              'processors: {}'.format(
                                  ", ".join(sorted(library)))))
    parser.add_argument('--log-level', dest='log_level',
                        default='info',
                        choices=sorted(levels.keys(), key=lambda l: levels[l]))

    args = parser.parse_args()

    set_level(args.log_level)

    calf = Calf(cluster=args.cluster,
                path=args.path,
                sentry_dsn=args.sentry_dsn,
                processors=args.processors)
    calf.run()


if __name__ == '__main__':
    main()
