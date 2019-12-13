from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.utils import timezone

import logging
import datetime
from face_recognition.utils.cors import cors_wide_open, add_response_headers, WIDE_OPEN_CORS
from face_recognition.recognitionapp.models import ProviderId
from face_recognition.presenceapp.models import FacePresenceHistory
from face_recognition.recognitionapp.models import FacePhoto
from face_recognition.recognitionapp.developer_workstations import map_to_developer_workstation

logger = logging.getLogger(__name__)


def _workstation_faces_list(workstation_id, minutes=10, min_seen_times=3):

    start_at = timezone.now() - datetime.timedelta(minutes=minutes)
    qs = FacePresenceHistory.objects.filter(workstation_id=workstation_id.lower(),
                                            created_at__gt=start_at,
                                            seen_times__gte=min_seen_times).order_by('-created_at')

    faces = []

    cache = {}

    for o in qs:
        if o.face_id in cache:
            continue
        face_data = o.as_dict()
        faces.append(face_data)
        cache[o.face_id] = face_data

    for pid in ProviderId.objects.filter(
            face_id__in=[f['face_id'] for f in faces],
            provider__in=(ProviderId.Provider.ARM_GUID, )):
        if pid.provider == ProviderId.Provider.ARM_GUID:
            cache[pid.face_id]['arm_guid'] = pid.inner_id
        elif pid.provider == ProviderId.Provider.MAILRU_VISION:
            cache[pid.face_id]['mrv_id'] = pid.inner_id

    response = {
        'faces': faces,
        'from': start_at
    }

    return response


def _workstation_face_visits_list(workstation_id, face_id, min_seen_times=2):

    qs = FacePresenceHistory.objects.filter(workstation_id=workstation_id.lower(),
                                            face_id=face_id,
                                            seen_times__gte=min_seen_times).order_by('-minute_slot')

    qs = qs[:1000]

    response = {
        'visits': [o.as_dict(short=False, url=False) for o in qs]
    }

    #    from face_recognition.recognitionapp.models import FacePhoto
    #    r['images'] = [o.as_dict() for o in FacePhoto.objects.filter(face_id=self.face_id).order_by('-id')[:images]]

    return response


def _face_image_list(face_id):
    qs = FacePhoto.objects.filter(face_id=face_id).order_by('-modified_at')
    qs = qs[:1000]

    response = {
        'photos': [o.as_dict(short=False, url=False) for o in qs]
    }

    return response


@cors_wide_open
def workstation_faces_list(request):
    """
    Выдать список лиц в указанной workstation
    :param request:
    :return:
    """
    workstation_id = request.GET.get('workstation_id').lower()
    workstation_id = map_to_developer_workstation(workstation_id)
    minutes = request.GET.get('minutes', '10')
    min_seen_times = request.GET.get('seen_times', '2')

    r = _workstation_faces_list(workstation_id=workstation_id,
                                minutes=int(minutes),
                                min_seen_times=int(min_seen_times))

    resp = JsonResponse(r)
    resp["Access-Control-Allow-Origin"] = "*"
    return resp


def workstation_faces_list_html(request):
    """
    Выдать список лиц в указанной workstation

    :param request:
    :return:
    """
    workstation_id = request.GET.get('workstation_id')
    workstation_id = map_to_developer_workstation(workstation_id)
    minutes = request.GET.get('minutes', '10')
    min_seen_times = request.GET.get('seen_times', '2')

    data = _workstation_faces_list(workstation_id=workstation_id, minutes=int(minutes), min_seen_times=int(min_seen_times))

    template = loader.get_template('faces_list.html')
    context = {
        'data': data,
        'workstation_id': workstation_id
    }
    return HttpResponse(template.render(context, request))


@cors_wide_open
def workstation_face_visits_list(request):
    """
    Выдать список визитов лица в указанной workstation
    :param request:
    :return:
    """
    workstation_id = request.GET.get('workstation_id')
    face_id = request.GET.get('face_id')

    r = _workstation_face_visits_list(workstation_id=workstation_id, face_id=face_id)

    resp = JsonResponse({'response': r})
    return resp


def workstation_face_visits_list_html(request):
    """
    Выдать список визитов лица в указанной workstation

    :param request:
    :return:
    """
    workstation_id = request.GET.get('workstation_id')
    face_id = request.GET.get('face_id')

    data = _workstation_face_visits_list(workstation_id=workstation_id, face_id=face_id)

    template = loader.get_template('face_visits_list.html')
    context = {
        'data': data,
        'workstation_id': workstation_id
    }
    return HttpResponse(template.render(context, request))




