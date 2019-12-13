# encoding: utf-8
from __future__ import unicode_literals, absolute_import, print_function

import re
import time
from flask import request
from flask import _app_ctx_stack as stack
from ... import metrics

# Based on: https://github.com/gfreezy/Flask-Statsd/blob/master/flask_statsd.py


def _extract_request_path(url_rule):
    if not url_rule:
        return ''
    s = re.sub(r'/<.*>', '/', str(url_rule))
    s = re.sub(r'\.json$', '', s)
    segments = filter(None, s.split('/'))
    return '_'.join(segments) if segments else '_'


class FlaskMetrics(object):

    def __init__(self, app, prefix='flask'):
        self.app = app
        self.prefix = prefix
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.before_request(self.before_request)
        app.after_request(self.after_request)

    def before_request(self):
        ctx = stack.top
        ctx.request_begin_at = time.time()

    def after_request(self, resp):
        ctx = stack.top
        period = (time.time() - ctx.request_begin_at) * 1000
        status_code = resp.status_code
        path = _extract_request_path(request.url_rule or 'notfound')
        path = self.prefix + '.' + path + '.' + 'http_%s' % status_code
        with metrics.pipeline() as pipe:
            pipe.incr(path)
            pipe.timing(path, period)
        return resp
