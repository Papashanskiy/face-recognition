# encoding: utf-8
import dlib
import cv2
import logging

# Docs:
# Install dlib: https://www.learnopencv.com/install-dlib-on-macos/

logger = logging.getLogger(__name__)


def crop_image_with_padding(img, x, y, x2, y2, padding=0.6):
    """
    Обрезать картинку по x, y, w, h, отступив на padding во все стороны
    """
    h=y2-y
    w=x2-x
    top = bottom = int(h * padding)
    left = right = int(w * padding)
    # return img[y:y + w, x:x + h]
    logger.info('crop_image_with_padding: %s %s %s %s %s', y - top, y + h + bottom, x - left, x + w + right, img.size)
    print('crop_image_with_padding: {} {} {} {} {}'.format(y - top, y + h + bottom, x - left, x + w + right, img.size))
    return img[y - top:y + h + bottom, x - left:x + w + right]


class FaceDetector(object):

    def __init__(self):
        self.detector = dlib.get_frontal_face_detector()

    def detect(self, img):
        if len(img):
            # print class_name, frame_no, n
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            for face_no, rect in enumerate(self.detector(gray, 1)):
                d = rect
                print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(
                    face_no, d.left(), d.top(), d.right(), d.bottom()))
                # rect= [(101, 22) (137, 58)]
                # Detection 0: Left: 101 Top: 22 Right: 137 Bottom: 58
                [x1, y1, x2, y2] = [d.left(), d.top(), d.right(), d.bottom()]
                face_img = crop_image_with_padding(img, x1, y1, x2, y2)
                yield [x1, y1, x2-x1, y2-y1], face_img
