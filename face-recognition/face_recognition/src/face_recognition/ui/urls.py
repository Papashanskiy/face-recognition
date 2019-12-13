from django.conf.urls import include, url

from .views import widget_css, widget_js

urlpatterns = [
    url(r'^faceid/1/widget.js$', widget_js),
    url(r'^faceid/1/widget.css$', widget_css),
]
