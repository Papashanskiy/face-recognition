import hug

import localapi.views.api
import localapi.views.ui

import logging


@hug.extend_api()
def with_other_apis():
    # Это конешно пиздец какой-то
    return [localapi.views.api, localapi.views.ui]


logging.basicConfig(level=logging.DEBUG)
