import datetime
import logging
from io import BytesIO

import pytz
from PIL import Image
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django.views.generic import View
from django_statsd.clients import statsd
from raven.contrib.django.models import get_client as get_raven_client

from face_recognition.presenceapp.models import FacePresenceHistory
from face_recognition.recognitionapp.connectors.mailru.vision import VisionAPI, RecognizeImage, RecognizedPerson
from face_recognition.recognitionapp.models import ProviderId, Face, FacePhoto

logger = logging.getLogger(__name__)


def crop_image_with_padding(img, coord, padding=(0.2, 0.6, 0.2, 0.2)):
    """
    Обрезать картинку по x, y, w, h, отступив на padding во все стороны
    """
    x, y, x2, y2 = coord
    h = y2 - y
    w = x2 - x
    left = int(w * padding[0])
    top = int(h * padding[1])
    right = int(w * padding[2])
    bottom = int(h * padding[3])

    coord = [
        max(x - left, 0),
        max(y - top, 0),
        min(x + w + right, img.width),
        min(y + h + bottom, img.height)
    ]
    return img.crop(coord)


def img_to_blob(img, format='jpeg'):
    buf = BytesIO()
    img.save(buf, format=format)
    return buf.getvalue()


class Recognizer(object):

    def __init__(self):
        self.vision_api = VisionAPI()

    def recognize(self, file, source_label=None):
        """
        Распознаём лица на картинке `file`.
        Отправляем картинку в vision api mcs.mail.ru и возвращаем id лица + координаты лица на картинке

        :param file: файл с картинкой
        :param source_label: метка источника, для наших метрик (например workstation_id)
        :return:
        """

        statsd.incr('mcs_call.{}'.format(source_label or 'UNK'), 1)
        logger.info('Recognizer.recognize lbl=%s', source_label)

        r = self.vision_api.recognize_one(
            RecognizeImage(name='1.jpg', data=file),
            create_new=True
        )
        # r = {'objects': [{'status': 0, 'name': '1.jpg',
        # 'persons': [{'tag': 'person2', 'coord': [105, 40, 389, 409], 'confidence': 0.99998, 'awesomeness': 0.4683}]}],
        # 'aliases_changed': False}
        logger.info('Recognizer.recognize response.body=%s', r.body)
        get_raven_client().extra_context({'mailru_response': r.body})
        return RecognizedPerson.from_response(r)

    def save_face_image(self, face_id, image, awesomeness, workstation_id=None):

        # Для mvp храним одну фотку человека, выбираем лучшую по awsomeness
        # TODO: хранить несколько фоток, за разные периоды времени
        image_blob = img_to_blob(image)
        new_photo = FacePhoto.objects.create(face_id=face_id,
                                             awesomeness=awesomeness,
                                             image_blob=image_blob,
                                             wh=image.width * image.height,
                                             workstation_id=workstation_id)

        # Храним 5 лучших фоток за последние 12 часов
        # Фотки старше 12 часов не трогаем
        period_start = timezone.now() - datetime.timedelta(hours=12)
        awesome_photo_ids = FacePhoto.objects.filter(face_id=face_id, created_at__gt=period_start).order_by(
            '-awesomeness').values_list('id', flat=True)[:5]
        qs = FacePhoto.objects.filter(face_id=face_id, created_at__gt=period_start).exclude(id__in=awesome_photo_ids)
        qs.delete()
        return new_photo

    def process_face(self, image, provider, provider_inner_id, awesomeness, workstation_id, ts):
        logger.info("process_face image=%s provider=%s, provider_inner_id=%s workstation_id=%s awesomeness=%s",
                    image, provider, provider_inner_id, workstation_id, awesomeness)

        try:
            pid = ProviderId.objects.get(provider=provider, inner_id=provider_inner_id)
        except ProviderId.DoesNotExist:
            pid = None

        if not pid:
            face = Face()
            face.save()
            pid = ProviderId.objects.create(provider=provider, inner_id=provider_inner_id, face=face)
            new_face = True
        else:
            Face.objects.filter(id=pid.face_id).update(last_seen_at=timezone.now())
            new_face = False

        photo = self.save_face_image(face_id=pid.face_id, image=image, awesomeness=awesomeness,
                                     workstation_id=workstation_id)

        time = datetime.datetime.fromtimestamp(ts).replace(tzinfo=pytz.utc)

        updated = FacePresenceHistory.objects \
            .add_face_presence(workstation_id=workstation_id,
                               face_id=pid.face_id,
                               time=time)

        return {'face_id': pid.face_id, 'photo_id': photo.id, 'presence_new': not updated, 'face_new': new_face}

    def crop_by_coord(self, img, coord):
        # TODO: убрать эту функцию, заменить на `crop_image_with_padding`
        target_width = coord[2] - coord[0]
        target_height = coord[3] - coord[1]
        padding_top = int(target_height * 0.3)
        padding_left = int(target_width * 0.3)
        coord = [coord[0] - padding_left,
                 coord[1] - padding_top,
                 coord[2] + padding_left,
                 coord[3] + padding_top
                 ]
        return img.crop(coord)

    def process(self, image_file, camera_id, ts):
        """
        Обработать входящий файл:
        - выделить лица
        - вырезать лица из картинки и положить в модели recognitionapp.models.Face/FacePhoto/ProviderId
        :param image_file:
        :return:
        """

        workstation_id = settings.CAMERAID_TO_WORKSTATION.get(camera_id)['workstation_id']
        min_wh = settings.CAMERAID_TO_WORKSTATION.get(camera_id).get('min_photo_wh', 0)
        img = Image.open(image_file)

        image_file.seek(0)

        for person in recognizer.recognize(file=image_file, source_label=camera_id):
            image = crop_image_with_padding(img, person.coord)
            wh = image.width * image.height
            if min_wh and wh < min_wh:
                logger.info('image too small %s < %s, skip', wh, min_wh)
                continue

            result = self.process_face(image=image,
                                       provider=ProviderId.Provider.MAILRU_VISION,
                                       provider_inner_id=person.get_global_id(),
                                       awesomeness=person.awesomeness,
                                       workstation_id=workstation_id,
                                       ts=float(ts)
                                       )

            if result['face_new']:
                statsd.incr('face.{}.create'.format(camera_id or 'UNK'), 1)

            if result['presence_new']:
                statsd.incr('face.{}.presence'.format(camera_id or 'UNK'), 1)

            logger.debug("process result: %s", result)


recognizer = Recognizer()


class RecognizeView(View):

    def post(self, request):
        recognizer.process(image_file=request.FILES['image'],
                           camera_id=request.GET.get('camera_id'),
                           ts=request.GET.get('ts'))
        return JsonResponse({'status': 'ok'})
