import json
from importlib import import_module
try:
    from json import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

from .logging import log


def try_json(event, source):
    if event['message'].startswith('{"'):
        try:
            payload = json.loads(event['message'])
        except JSONDecodeError:
            log("error decoding json", raw_msg=event['message'], level='err')
            event['json_attempt'] = True
        else:
            event.update(payload)
    return event


library = {'json': try_json}


class LoadingError(Exception):
    pass


def load_processors(processors):
    loaded_procs = []
    for proc in processors:
        if proc in library:
            loaded_procs.append(library[proc])
        else:
            if '.' not in proc:
                raise LoadingError(
                    "Cannot find processor '{}'. Either specify one of the "
                    "available processors ({}) or the full dotted path to "
                    "your processor.".format(proc, ", ".join(sorted(library))))
            mod, attr = proc.rsplit('.', 1)
            module = import_module(mod)
            final_attr = getattr(module, attr)
            if isinstance(final_attr, (list, tuple)):
                loaded_procs.extend(final_attr)
            else:
                loaded_procs.append(final_attr)
    log("found processors",
        processors=[proc.__name__ for proc in loaded_procs])
    return loaded_procs
