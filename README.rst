Calf
====

A simple syslog-to-elasticsearch bridge with pluggable processing.

*Calf* expects a log format in the form of::

    DATE(RFC3339) logsource program[pid]: message

In Rsyslog, this can be achieved with the ``RSYSLOG_FileFormat`` format.

Installation
------------

Calf requires Python 3.4 or greater.

::

    pip install calf

Usage
-----

::

    calf

Command-line arguments:

* ``--cluster``: path to the ElasticSearch cluster. Default:
  ``http://localhost:9200``.
* ``--path``: path to syslog file to tail. Default: ``/var/log/syslog``.
* ``--processors``: list of processors for building a log processing pipeline.
  Can be from the built-in processors, or custom processors available in your
  Python path.

Built-in processors:

* ``json``: tries to decode the message as JSON.

Writing custom processors
-------------------------

Basics
``````

Each processor is a Python function that takes two argument: an ``event_dict``
and the raw log message.

The processor **must** return the event dict or ``None``. If ``None`` is
returned by a processor, the event is dropped.

.. code-block:: python

    def my_processor(event_dict, log_line):
        return event_dict


Once your processors are written, pass them to ``calf`` by using the dotted
path to your functions. E.g. assuming the processor above was written to
``custom_processors.py``::

    calf --processors custom_processors.my_processor

Registering all processors at once
``````````````````````````````````

It is also possible to point to a **list** of processors to avoid the tedious
process of passing all your processors in the command line. Simply construct a
list at the end of your custom processors definition:

.. code-block:: python

    all_processors = [
        my_processor,
        my_other_processor,
    ]

And pass this list to ``calf``::

    calf --processors custom_processors.all_processors

Base event data
```````````````

If you plan to do some heavier processing for specific messages (e.g. HTTP
logs), it can be useful to look at the base event data to avoid expensive
processing on irrelevant logs. The following attributes are available:

* ``source_host``: the host on which ``calf`` is run
* ``program``: the originating program
* ``message``: the actual message after syslog prefixes
* ``type`` and ``_type``: by default ``relp``. You can set it to something
  else if that eases processing.
* ``logsource``: host from which the log message was issued
* ``logsource2`` (not always present): sometimes, extended version of
  ``logsource``
* ``pid`` (not always present): the program PID, when available.

For instance, to parse HTTP logs:

.. code-block:: python

    def http_parser(event_dict, _):
        if event_dict['program'] != 'nginx':
            return event_dict
        else:
            # parse log & return a richer event_dict
            event_dict['_type'] = 'nginx'

If you add more data to a class of events (e.g. by program), it is recommended
to alter the event's ``_type`` to something unique for this events class.
Elasticsearch infers its mappings for each types and this avoids type
conflicts (e.g. if a field name ``transaction_id`` is either a ``long`` or a
``string`` for different event types).

License
-------

BSD.
