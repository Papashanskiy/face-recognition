from scipy.spatial import distance as dist
import numpy as np
from imutils import face_utils
import cv2

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]


def eye_aspect_ratio(eye):
    # compute the euclidean distances between the two sets of
    # vertical eye landmarks (x, y)-coordinates
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])

    # compute the euclidean distance between the horizontal
    # eye landmark (x, y)-coordinates
    C = dist.euclidean(eye[0], eye[3])

    # compute the eye aspect ratio
    ear = (A + B) / (2.0 * C)

    # return the eye aspect ratio
    return ear


EYE_AR_THRESH = 0.2


def eyes_are_closed(shape):
    # extract the left and right eye coordinates, then use the
    # coordinates to compute the eye aspect ratio for both eyes
    leftEye = shape[lStart:lEnd]
    rightEye = shape[rStart:rEnd]
    leftEAR = eye_aspect_ratio(leftEye)
    rightEAR = eye_aspect_ratio(rightEye)

    # average the eye aspect ratio together for both eyes
    ear = (leftEAR + rightEAR) / 2.0

    return ear < EYE_AR_THRESH


def eyes_angle(shape):
    leftEyePts = shape[lStart:lEnd]
    rightEyePts = shape[rStart:rEnd]
    # compute the center of mass for each eye
    leftEyeCenter = leftEyePts.mean(axis=0).astype("int")
    rightEyeCenter = rightEyePts.mean(axis=0).astype("int")
    # compute the angle between the eye centroids
    dY = rightEyeCenter[1] - leftEyeCenter[1]
    dX = rightEyeCenter[0] - leftEyeCenter[0]
    angle = np.degrees(np.arctan2(dY, dX)) - 180

    # compute center (x, y)-coordinates (i.e., the median point)
    # between the two eyes in the input image
    eyesCenter = ((leftEyeCenter[0] + rightEyeCenter[0]) // 2,
                  (leftEyeCenter[1] + rightEyeCenter[1]) // 2)

    return eyesCenter, angle


def align_eyes_angle(img, shape):
    # grab the rotation matrix for rotating and scaling the face
    eyesCenter, angle = eyes_angle(shape)
    M = cv2.getRotationMatrix2D(eyesCenter, angle, 1)
    (cols, rows, _) = img.shape
    dst = cv2.warpAffine(img, M, (cols, rows))
    return dst
