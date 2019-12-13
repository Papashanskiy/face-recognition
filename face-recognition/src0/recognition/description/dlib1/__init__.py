#   This example shows how to use dlib's face recognition tool.  This tool maps
#   an image of a human face to a 128 dimensional vector space where images of
#   the same person are near to each other and images from different people are
#   far apart.  Therefore, you can perform face recognition by mapping faces to
#   the 128D space and then checking if their Euclidean distance is small
#   enough.
#
#   When using a distance threshold of 0.6, the dlib model obtains an accuracy
#   of 99.38% on the standard LFW face recognition benchmark, which is
#   comparable to other state-of-the-art methods for face recognition as of
#   February 2017. This accuracy means that, when presented with a pair of face
#   images, the tool will correctly identify if the pair belongs to the same
#   person or is from different people 99.38% of the time.
#
#   Finally, for an in-depth discussion of how dlib's tool works you should
#   refer to the C++ example program dnn_face_recognition_ex.cpp and the
#   attendant documentation referenced therein.

import os

import cv2
import dlib
from imutils import face_utils

from core.image import shape_to_np
from .utils.eyes import eyes_are_closed, align_eyes_angle

THIS_DIR = os.path.abspath(os.path.dirname(__file__))


class EyesAreClosed(Exception):
    pass


class FaceDescriptor(object):

    def __init__(self):
        # Load all the models we need: a shape predictor
        # to find face landmarks so we can precisely localize the face and  the
        # face recognition model.
        data = lambda name: os.path.join(THIS_DIR, 'data', name)
        self.sp = dlib.shape_predictor(data('shape_predictor_68_face_landmarks.dat'))
        self.facerec = dlib.face_recognition_model_v1(data('dlib_face_recognition_resnet_model_v1.dat'))

    def draw_shape(self, img, shape):
        img = img.copy()
        for point in shape.parts():
            # img[point.x, point.y] = (0, 0, 200)
            # print("draw", (point.x, point.y))
            cv2.circle(img, (point.x, point.y), 1, (0, 255, 0), -1)
        return img

    def to_vector(self, img, debug=False, ignore_closed_eyes=True):
        """
        Возвращаем вектор, в данном случае 128 точек
        :param img:
        :return:
        """
        rect = dlib.rectangle(0, 0, img.shape[0], img.shape[1])
        shape = self.sp(img, rect)

        shape_np = shape_to_np(shape)

        if ignore_closed_eyes and eyes_are_closed(shape_np):
            raise EyesAreClosed()

        img_rotated = align_eyes_angle(img, shape_np)
        shape_rotated = self.sp(img_rotated, rect)

        if debug:
            #img_debug = face_utils.visualize_facial_landmarks(img_rotated, shape_to_np(shape_rotated))
            img_debug = self.draw_shape(img_rotated, shape_rotated)
        else:
            img_debug = img_rotated

        face_descriptor = self.facerec.compute_face_descriptor(img_rotated, shape_rotated)
        return img_debug, face_descriptor, shape_to_np(shape).tolist()
