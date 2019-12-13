from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseRedirect, Http404, HttpResponseForbidden
from django.core.exceptions import SuspiciousOperation
import logging
from django.views.generic import View
from face_recognition.utils.cors import cors_wide_open, add_response_headers, WIDE_OPEN_CORS
from face_recognition.recognitionapp.models import ProviderId, Face, FacePhoto
from face_recognition.presenceapp.models import FacePresenceHistory
from face_recognition.recognitionapp.developer_workstations import map_to_developer_workstation
from django_statsd.clients import statsd
from face_recognition.cameraregistryapp.registry import get_camera_id_by_workstation_id

logger = logging.getLogger(__name__)


@cors_wide_open
def face_get_main_image(request):
    """
    Выдать картинку по id
    :param request:
    :return:
    """

    id = request.GET.get('id')
    photo_id = request.GET.get('photo_id', None)
    arm_guid = request.GET.get('arm_guid', None)
    redirect_if_empty = request.GET.get('redirect_if_empty', None)
    workstation_id = request.GET.get('workstation_id', None)
    workstation_id = workstation_id.lower() if workstation_id else None
    workstation_id = map_to_developer_workstation(workstation_id)
    fmt = request.GET.get('fmt', 'image')

    logger.info('face_get_main_image: arm_guid=%s workstation_id=%s fmt=%s',
                arm_guid, workstation_id, fmt)

    metric_name = 'face.{}.get_image'.format(get_camera_id_by_workstation_id(workstation_id, 'UNK'))
    statsd.incr(metric_name + '.total', 1)

    if arm_guid:
        metric_name = metric_name + '.arm_guid'
    elif id:
        metric_name = metric_name + '.id'
    elif photo_id:
        metric_name = metric_name + '.photo_id'

    if arm_guid:
        if id:
            return HttpResponseBadRequest('should be only one id: `id` or `arm_guid`')
        arm_guid = arm_guid.lower()
        face = None
        for p in ProviderId.objects.filter(provider=ProviderId.Provider.ARM_GUID, inner_id=arm_guid).order_by('-modified_at'):
            face = p.face
            break
        if not face:
            statsd.incr(metric_name + '.404', 1)
            if redirect_if_empty:
                return HttpResponseRedirect(redirect_to=redirect_if_empty)
            logger.debug('no images found for arm_guid %s', arm_guid)
            raise Http404()
        id = face.id

    qs = FacePhoto.objects.filter(face_id=int(id))
    if photo_id:
        qs = qs.filter(id=int(photo_id))
    photos = qs.order_by('-awesomeness')[:5]

    if not FacePresenceHistory.objects.has_presence(face_id=id, workstation_id=workstation_id):
        # raise SuspiciousOperation('face not present in this workstation')
        logger.error('face from another workstation. request: arm_guid=%s workstation_id=%s', arm_guid, workstation_id)
        statsd.incr(metric_name + '.403', 1)
        return HttpResponseForbidden('face from another workstation')

    if fmt == 'image':
        if photos:
            photo = photos[0]
            response = HttpResponse(content_type="image/jpg")
            #filename = '{}-{}.jpg'.format(id, photo.pk)
            #response['Content-Disposition'] = 'attachment; filename=%s' % filename
            response.write(photo.image_blob)
            statsd.incr(metric_name + '.200', 1)
            return response
        else:
            statsd.incr(metric_name + '.410', 1)
            return JsonResponse({'status': 'error'}, status=410)

    elif fmt == 'json':
        statsd.incr(metric_name + '.200', 1)
        return JsonResponse({
            'id': int(id),
            'status': 'ok',
            'photos_count': photos.count(),
            'photos': [p.as_dict() for p in photos]
        })

    statsd.incr(metric_name + '.400', 1)
    return JsonResponse({'status': 'error', 'description': 'invalid `fmt` value'}, status=400)


class FaceSetIdView(View):

    def parse(self, request):

        self.face_id = request.GET.get('id') or request.GET.get('face_id')
        self.provider_name = request.GET.get('provider_name', None)
        self.provider_id = request.GET.get('provider_id', None)
        self.workstation_id = request.GET.get('workstation_id', None)
        self.workstation_id = map_to_developer_workstation(self.workstation_id)

        if not (self.face_id and self.provider_name and self.provider_id and self.workstation_id):
            raise SuspiciousOperation('id and provider_name and provider_id and workstation_id required')

        if not FacePresenceHistory.objects.has_presence(face_id=self.face_id, workstation_id=self.workstation_id):
            raise SuspiciousOperation('face not present in this workstation')

        PROVIDERS = {
            'arm_guid': ProviderId.Provider.ARM_GUID
        }

        self.provider = PROVIDERS.get(self.provider_name)
        if self.provider is None:
            raise SuspiciousOperation('invalid provider_name')

    def options(self, request, *args, **kwargs):
        response = super(FaceSetIdView, self).options(request, *args, **kwargs)
        add_response_headers(response, headers=WIDE_OPEN_CORS)
        return response

    def post(self, request):
        """
        Сохранить внешний идентификатор для лица, например гуид арма

        :param request:
        :return:
        """

        try:
            self.parse(request)
        except SuspiciousOperation as exc:
            return HttpResponseBadRequest(str(exc))

        _, created = ProviderId.objects.set_id(
            face_id=self.face_id,
            provider=self.provider,
            provider_id=self.provider_id.lower()
        )

        metric_name = 'face.{}.set_guid'.format(get_camera_id_by_workstation_id(self.workstation_id, 'UNK'))
        statsd.incr(metric_name, 1)

        response = JsonResponse({'status': 'ok', 'created': created})
        add_response_headers(response, headers=WIDE_OPEN_CORS)
        return response

    def delete(self, request):
        """
        Удалить внешний идентификатор для лица, например гуид арма

        :param request:
        :return:
        """

        self.parse(request)

        r = ProviderId.objects.filter(
            face_id=self.face_id,
            provider=self.provider,
            inner_id=self.provider_id.lower()
        ).delete()

        metric_name = 'face.{}.delete_guid'.format(get_camera_id_by_workstation_id(self.workstation_id, 'UNK'))
        statsd.incr(metric_name, 1)

        response = JsonResponse({'response': {'deleted': bool(r)}})
        add_response_headers(response, headers=WIDE_OPEN_CORS)
        return response
