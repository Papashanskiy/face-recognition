# encoding: utf-8
from __future__ import absolute_import
import logging
from .helpers import get_instance


class App(object):

    obj = None

    def __init__(self, backend='object_detector.metrics.dummy.DummyMetricsBackend', options=None):
        if backend:
            self.init(backend, options)

    def init(self, backend_name, backend_options=None):
        logging.info('metrics init %s %s', backend_name, backend_options)
        self.obj = get_instance(backend_name, backend_options or {})


app = App()


def incr(*args, **kwargs):
    app.obj.incr(*args, **kwargs)


def timing(*args, **kwargs):
    app.obj.timing(*args, **kwargs)


def set(*args, **kwargs):
    app.obj.set(*args, **kwargs)


def gauge(*args, **kwargs):
    app.obj.gauge(*args, **kwargs)


def pipeline():
    return app.obj.pipeline()
