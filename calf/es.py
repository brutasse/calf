import json

import requests

from .logging import log
from .utils import chunked

INDEX_TEMPLATE = 'logstash-%Y.%m.%d'
_template = {
    "template": "logstash-*",
    "settings": {
        "index.refresh_interval": "5s"
    },
    "mappings": {
        "_default_": {
            "_all": {"enabled": True,
                     "omit_norms": True},
            "dynamic_templates": [{
                "message_field": {
                    "match": "message",
                    "match_mapping_type": "string",
                    "mapping": {
                        "type": "string",
                        "index": "analyzed",
                        "omit_norms": True,
                    },
                },
            }, {
                "string_fields": {
                    "match": "*",
                    "match_mapping_type": "string",
                    "mapping": {
                        "type": "string",
                        "index": "analyzed",
                        "omit_norms": True,
                        "fields": {
                            "raw": {
                                "type": "string",
                                "index": "not_analyzed",
                                "ignore_above": 256,
                            },
                        },
                    },
                },
            }],
            "properties": {
                "@version": {
                    "type": "string",
                    "index": "not_analyzed",
                },
                "geoip": {
                    "type": "object",
                    "dynamic": True,
                    "properties": {
                        "location": {"type": "geo_point"},
                    },
                },
            },
        },
    },
}


def wait_for_status(cluster, color='yellow'):
    url = '{}/_cluster/health'.format(cluster)
    response = requests.get(url, params={'wait_for_status': color})
    response.raise_for_status()


def ensure_index_template(cluster):
    wait_for_status(cluster)
    url = '{}/_template/logstash'.format(cluster)
    response = requests.post(url, json=_template)
    response.raise_for_status()


def send_batch(cluster, events, chunk_size=500):
    url = '{}/_bulk'.format(cluster)
    for chunk in chunked(events, chunk_size):
        payload = []
        for event in chunk:
            payload.append(json.dumps(
                {'index': {'_index': event.pop('_index'),
                           '_type': event.pop('_type')}}))
            payload.append(json.dumps(event))
        payload.append("")
        data = "\n".join(payload)
        wait_for_status(cluster)
        log("sending lines", lines_count=len(chunk), cluster=cluster,
            bytes_length=len(data), level='debug')
        response = requests.post(url, data=data)
        response.raise_for_status()
