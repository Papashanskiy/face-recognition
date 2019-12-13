from celery import Celery
from celery.utils.log import get_task_logger
import settings
from core import db
from core.image import normalize_intensity, resize_image, np_to_jpeg
from skimage import io
import numpy as np
import cv2
import logging
from recognition.description.dlib1 import FaceDescriptor, EyesAreClosed

logger = get_task_logger(__name__)

app = Celery(__name__)

imagedb = db.Image()
descriptordb = db.ImageDescriptor()
masterimagedb = db.ImageMaster()

descriptor = FaceDescriptor()


def calculate_vector(img, debug=False):
    frame = cv2.imdecode(img, cv2.IMREAD_COLOR)
    frame = normalize_intensity(frame)
    frame = resize_image(frame, size=settings.FACE_SIZE)

    img, vector, shape = descriptor.to_vector(frame, debug=debug, ignore_closed_eyes=True)

    return list(vector), img, shape


@app.task(name='recognition.calc_descriptor')
def calc_descriptor(image_id, debug=True, merge=True):
    """
    :param id:
    :return:
    """
    # print("image_id={}".format(image_id))
    blob = imagedb.load(id=image_id)['image']
    img = np.asarray(bytearray(blob), dtype=np.uint8)

    try:
        vector, debug_img, shape = calculate_vector(img, debug=debug)
    except EyesAreClosed:
        logger.warn('EyesAreClosed, skip image')
        imagedb.delete(id=image_id)
        return

    imagedb.add_debug_image(id=image_id, img=np_to_jpeg(debug_img), shape={'v': '1', 'sh': shape})
    descriptordb.save(image_id, descriptor=vector)
    if merge:
        merge_image.delay(image_id=image_id, vector=vector)
    return vector


@app.task(name='recognition.merge_image')
def merge_image(image_id, vector):
    """
    Найти похожие лица и сохранить информацию о связи

    :param image_id:
    :return:
    """

    master_id, created = masterimagedb.merge_or_create(image_id, vector, max_distance=0.55)
    if created:
        logger.info('New master image %s', master_id)
    else:
        logger.info('Merged with master image %s -> %s', image_id, master_id)
    imagedb.set_master(image_id, master_id)
    descriptordb.set_master(image_id, master_id)
    return master_id


def configure(**kwargs):
    global app
    for k, v in kwargs.items():
        if v is not None:
            setattr(settings, k, v)
    app.config_from_object(settings)


configure()