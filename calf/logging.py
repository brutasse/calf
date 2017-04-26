import json
import syslog

levels = {level: getattr(syslog, 'LOG_{}'.format(level.upper()))
          for level in ['emerg', 'alert', 'crit', 'err', 'warning', 'notice',
                        'info', 'debug']}

log_level = levels['info']


def set_level(level):
    global log_level
    log_level = levels[level]


def log(msg, level='info', **kwargs):
    pri = getattr(syslog, 'LOG_{}'.format(level.upper()), syslog.LOG_INFO)
    if pri <= log_level:
        kwargs.update({
            'event': msg,
            '_type': 'calf',
        })
        syslog.syslog(pri, json.dumps(kwargs, separators=(',', ':')))
