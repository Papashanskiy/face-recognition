# encoding: utf-8
from __future__ import unicode_literals, absolute_import, print_function
from functools import wraps
from time import time

from . import app


def time_and_count_metrics(instance):
    """
    Декоратор функции для отправки метрик:
    - количество вызовов
    - количество ошибок
    - тайминг
    :param instance:string - префикс для метрики
    :return:
    """
    def deco(func):
        time_key = '{}.{}.time'.format(instance, func.__name__)
        error_key = '{}.{}.error'.format(instance, func.__name__)
        call_key = '{}.{}.call'.format(instance, func.__name__)
        func._metrics = None

        @wraps(func)
        def inner(*args, **kwargs):
            metrics = func._metrics
            if metrics is None:
                func._metrics = metrics = app.obj
            if metrics:
                t0 = time()
                try:
                    metrics.set(call_key, 1)
                    ret = func(*args, **kwargs)
                    metrics.timing(time_key, 1000000*(time()-t0))  # µs - микросекунда
                    return ret
                except Exception as e:
                    metrics.set(error_key, 1)
                    raise
        return inner
    return deco
