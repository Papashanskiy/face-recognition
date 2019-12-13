from django.conf.urls import include, url
from django.contrib import admin

from .views import workstation_faces_list, workstation_faces_list_html, workstation_face_visits_list_html, workstation_face_visits_list

urlpatterns = [
    url(r'^workstation/faces$', workstation_faces_list),
    url(r'^workstation/faces.html$', workstation_faces_list_html),
    url(r'^workstation/face/visits$', workstation_face_visits_list, name='face-visits-json'),
    url(r'^workstation/face/visits.html$', workstation_face_visits_list_html, name='face-visits-html'),
    url(r'^admin/$', admin.site.urls),
]
