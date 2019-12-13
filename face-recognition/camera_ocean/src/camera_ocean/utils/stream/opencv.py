import cv2
import imutils
from imutils.video import FPS
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class MyFPS(FPS):
    def elapsed(self):
        if self._end:
            return super(MyFPS, self).elapsed()
        else:
            return (datetime.now() - self._start).total_seconds()

def np_to_jpeg(img):
    try:
        _, buf = cv2.imencode('.jpg', img)
    except cv2.error:
        return None
    return buf.tobytes()


def too_much_difference(frm1, frm2, threshold=0.5):

    if frm1 is not None and frm2 is not None:
        dff = cv2.absdiff(frm1, frm2)
        w, h = dff.shape[:2]
        s = dff.sum()
        k = s / (w * h)
        if k > threshold:
            logging.info('too_much_difference s=%s w=%s h=%s k=%s', s, w, h, k)
            return True

    return False


class VideoStream(object):
    def __init__(self, path, sample_rate=1, resize_width=None, rotate=None, grayscale=False, crop=None,
                 current_image_store=None):
        self.stream = cv2.VideoCapture(path)
        self.sample_rate = sample_rate
        self.fps = MyFPS()
        self.resize_width = resize_width
        self.rotate = rotate
        self.grayscale = grayscale
        self.current_image_store = current_image_store
        self.crop = crop

    def __del__(self):
        self.stream.release()

    def iter_frames(self):
        self.fps.start()
        n = 0
        grayscale = self.grayscale
        rotate = self.rotate
        resize_width = self.resize_width
        sample_rate = self.sample_rate or 24
        crop = self.crop
        fps = self.fps
        prev_frame = None
        frame = None

        while self.stream.isOpened():
            n += 1

            ret, frame = self.stream.read()
            if not ret:
                break

            #if too_much_difference(prev_frame, frame):
            #    logger.info('frames too different, skip')
            #    prev_frame = frame
            #    continue

            prev_frame = frame

            if n % sample_rate != 0:
                continue
            fps.update()
            logger.debug('get frame %s, fps: %0.2f', n, self.fps.fps())
            # print("frame_no:", n, ret)

            if crop:
                x1, x2 = crop[0], crop[2]
                y1, y2 = crop[1], crop[3]
                frame = frame[y1:y2, x1:x2]

            if resize_width:
                frame = imutils.resize(frame, width=resize_width)

            if rotate:
                frame = imutils.rotate_bound(frame, 6)

            if grayscale:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            jpeg = np_to_jpeg(frame)

            if self.current_image_store:
                self.current_image_store.save(jpeg)

            yield {'frame': frame, 'jpeg': jpeg }

    def __iter__(self):
        try:
            for frame in self.iter_frames():
                yield frame
        finally:
            self.fps.stop()
            print("[INFO] elasped time: {:.2f}".format(self.fps.elapsed()))
            print("[INFO] approx. FPS: {:.2f}".format(self.fps.fps()))
