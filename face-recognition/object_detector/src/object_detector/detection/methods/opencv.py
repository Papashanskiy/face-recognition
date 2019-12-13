# encoding: utf-8
import cv2
import os
import settings
import logging

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def crop_image_with_padding(img, x, y, w, h, padding=0.2):
    """
    Обрезать картинку по x, y, w, h, отступив на padding во все стороны
    """
    top = bottom = int(h * padding)
    left = right = int(w * padding)
    # return img[y:y + w, x:x + h]
    return img[y - top:y + h + bottom, x - left:x + w + right]


class FaceDetector(object):

    def __init__(self):
        pass

    def detect(self, img):
        # convert the test image to gray scale as opencv face detector expects gray images
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # load OpenCV face detector, I am using LBP which is fast
        # there is also a more accurate but slow: Haar classifier

        face_cascade = cv2.CascadeClassifier(os.path.join(THIS_DIR, 'opencv-files/lbpcascade_frontalface.xml'))

        # let's detect multiscale images(some images may be closer to camera than others)
        # result is a list of faces
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5);

        for coords in faces:
            (x, y, w, h) = coords
            if w < settings.MINIMUM_FACE_SIZE:
                # Слишком маленькие лица игноируем
                logging.warning('ignore small face with size %s %s', w, h)
                continue
            yield (x, y, w, h), crop_image_with_padding(gray, x,y,w,h, padding=0.1) # gray[y:y + w, x:x + h]
