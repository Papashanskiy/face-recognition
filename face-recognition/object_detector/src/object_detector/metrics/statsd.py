# encoding: utf-8
from __future__ import absolute_import

__all__ = ['StatsdMetricsBackend']

import statsd
import socket

from .base import MetricsBackend


def clear_key(key):
    return key.replace('.', '_')


def add_tags(path, tags):
    if not tags:
        return path
    tag_str = ','.join([('%s=%s' % (k, v)) for k, v in tags.items()])
    return '%s,%s' % (path, tag_str)


class StatsdMetricsBackend(MetricsBackend):
    def __init__(self, host='localhost', port=8125, add_hostname=True, **kwargs):
        self.client = statsd.StatsClient(host=host, port=port)
        if add_hostname:
            hostname = clear_key(socket.gethostname())
            prefix = kwargs.get('prefix')
            prefix = ".".join(filter(None, [prefix, hostname]))
            if prefix and not prefix.endswith('.'):
                prefix += '.'
            kwargs['prefix'] = prefix
        super(StatsdMetricsBackend, self).__init__(**kwargs)

    def _full_key(self, key, instance=None, tags=None):
        if instance:
            key = '{}.{}'.format(key, instance)
        if tags:
            key = add_tags(key, tags)
        return key

    def incr(self, key, instance=None, tags=None, amount=1, sample_rate=1):
        self.client.incr(self._full_key(self._get_key(key), tags=tags), amount, sample_rate)

    def timing(self, key, value, instance=None, tags=None, sample_rate=1):
        self.client.timing(self._full_key(self._get_key(key), tags=tags), value, sample_rate)

    def set(self, key, instance=None, tags=None, amount=1, sample_rate=1):
        self.client.set(self._full_key(self._get_key(key), tags=tags), value=amount, rate=sample_rate)

    def gauge(self, key, value, instance=None, tags=None, sample_rate=1):
        self.client.gauge(self._full_key(self._get_key(key), tags=tags), value=value, rate=sample_rate)

    def pipeline(self):
        # todo: сделать работающий пайплайн (сейчас он ничего не пайплайнит)
        return self
