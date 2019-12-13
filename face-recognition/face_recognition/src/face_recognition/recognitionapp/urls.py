from django.conf.urls import include, url

from .views import RecognizeView
from .views.face import face_get_main_image, FaceSetIdView

urlpatterns = [
    url(r'^image$', RecognizeView.as_view()),
    url(r'^face/image$', face_get_main_image, name='face-image'),
    url(r'^face/set-id$', FaceSetIdView.as_view(), name='face-set-id'),
]
