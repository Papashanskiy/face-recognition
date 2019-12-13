import datetime
import logging
import os
import time
from io import BytesIO
import random

from raven.contrib.flask import Sentry
import environ  # django-environ
import numpy
import requests
from PIL import Image
from flask import Flask, request, make_response

from object_detector.detection.methods.dlib import FaceDetector
from object_detector.metrics.middleware.flask import FlaskMetrics
from object_detector import metrics

logger = logging.getLogger(__name__)

env = environ.Env(
    TMP_IMAGE_PATH=(str, '/tmp')
)


class ObjectDetector(object):

    def __init__(self):
        self.detector = FaceDetector()

    def detect(self, frame):
        t0 = time.time()
        faces = [{'image': img, 'box': rect} for rect, img in self.detector.detect(frame)]
        logger.info("detector.detect: %s faces in %0.2f sec", len(faces), time.time() - t0)
        return faces


class ImageSender(object):

    def __init__(self, url, **kwargs):
        self.url = url
        self.session = requests.Session()

    def send(self, image, params=None):
        t0 = time.time()
        r = self.session.post(url=self.url, files={'image': image}, params=params)
        logger.info('sent image to %s size %s in %0.2f sec', self.url, len(image), time.time() - t0)


app = Flask(__name__)
sentry = Sentry(app, dsn='http://b80bd919c3994bfcaa78d3da0623cdbd:1171ddcc3b3443ed93393f66a413a3aa@sv-mt06.invitro.ru/15')

metrics.app.init(
    'object_detector.metrics.statsd.StatsdMetricsBackend',
    dict(host='172.17.16.115', port=8125, prefix='facerec.obj')
)
FlaskMetrics(app)

detector = ObjectDetector()
sender = ImageSender(url=env('URL', default='http://127.0.0.1:8777/recognize/image'))

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(module)s %(process)d %(message)s'
)


def image_from_array(data):
    try:
        face_img = Image.fromarray(data)
    except ValueError:
        logger.exception('error in image_from_array, shape=%s', data.shape)
        return None
    return face_img


def save_debug_img(data, camera_id, prefix='image', sample=1.0):
    if sample < 1:
        if random.random() > sample:
            return
    tmpfn = '{}-{}.jpg'.format(prefix, datetime.datetime.now().strftime('%Y%m%d%H%M'))
    tmpdir = os.path.join(env('TMP_IMAGE_PATH'), str(camera_id))
    os.makedirs(tmpdir, exist_ok=True)
    with open(os.path.join(tmpdir, tmpfn), 'wb') as tmpf:
        tmpf.write(data)


def detect_objects_on_image(f):
    ret = []
    img = Image.open(f)
    frame = numpy.array(img)
    for face in detector.detect(frame):
        face_img = image_from_array(face['image'])
        if face_img is None:
            continue
        buf = BytesIO()
        face_img.save(buf, 'jpeg')
        ret.append(buf.getvalue())
    return ret



@app.route('/process/image', methods=['POST'])
def process_image():
    """
    Основная функция микросервисы object-deteсtor - определять наличие [любого] лица на фотке/кадре.
    Если лицо есть, то фотку надо отправить дальше на обработку.
    Если лица нет, то огнорить её.
    :return:
    """
    camera_id = request.args.get('camera_id')
    ts = request.args.get('ts')
    frame_id = request.args.get('frame_id')

    logger.info('process_image camera_id=%s ts=%s frame_id=%s',
                camera_id, ts, frame_id)

    f = request.files['data']

    file_data = f.read()
    f.seek(0)

    send_images = detect_objects_on_image(f)

    if send_images:
        save_debug_img(file_data, camera_id=camera_id, prefix='face')
    else:
        save_debug_img(file_data, camera_id=camera_id, prefix='noface', sample=0.1)

    for image in send_images:
        sender.send(image=image, params={'camera_id': camera_id, 'ts': ts})

    resp = make_response('OK', 200)
    # resp.headers['X-Header'] = 1

    return resp
