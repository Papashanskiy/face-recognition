# encoding: utf-8
from __future__ import absolute_import
from random import random
from threading import local

__all__ = ['MetricsBackend']


class MetricsBackend(local):
    def __init__(self, prefix=None):
        self.prefix = prefix

    def _get_key(self, key):
        if self.prefix:
            return '{}{}'.format(self.prefix, key)
        return key

    def _sanitize_key(self, key):
        return key

    def _should_sample(self, sample_rate):
        return sample_rate >= 1 or random() >= 1 - sample_rate

    def incr(self, key, instance=None, tags=None, amount=1, sample_rate=1):
        raise NotImplementedError

    def timing(self, key, value, instance=None, tags=None, sample_rate=1):
        raise NotImplementedError

    def set(self, stat, value, instance=None, tags=None, sample_rate=1):
        raise NotImplementedError

    def gauge(self, stat, value, instance=None, tags=None, sample_rate=1):
        raise NotImplementedError

    def pipeline(self):
        return self

    def __enter__(self):
        return self

    def __exit__(self, typ, value, tb):
        pass
