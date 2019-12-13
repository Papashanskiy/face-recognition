# encoding: utf-8
import os
import logging
import time
import requests

from camera_ocean.utils.stream.opencv import VideoStream
from camera_ocean.utils.logger import raven_client

logger = logging.getLogger(__name__)


class ImageReader(object):
    """
    Универсальный читатель картинок.
    Может читать из rtsp-потока камеры, из видеофайла на диске, из папки с картинками.
    """

    def __init__(self, path=None,
                 resize_width=None,
                 rotate=None,
                 grayscale=False,
                 sample_rate=1,
                 current_image_store=None,
                 forever=False,
                 crop=None):
        self.path = path
        self.resize_width = resize_width
        self.rotate = rotate
        self.grayscale = grayscale
        self.sample_rate = sample_rate
        self.current_image_store = current_image_store
        self.forever = forever
        self.crop = crop

    def iter_video_sources(self):
        sources = []
        if isinstance(self.path, int):
            sources.append(self.path)
        elif ('*' in self.path or '?' in self.path) and ('://' not in self.path):
            import glob
            sources.extend(glob.glob(self.path))
        else:
            sources.append(self.path)
        for src in sources:
            print('stream from source: ', src)
            yield VideoStream(path=src,
                              resize_width=self.resize_width,
                              rotate=self.rotate,
                              grayscale=self.grayscale,
                              crop=self.crop,
                              sample_rate=self.sample_rate,
                              current_image_store=self.current_image_store)

    def _iter_frames(self):

        for stream in self.iter_video_sources():

            for data in stream:
                # data = {'frame': <numpy array>, 'jpeg': <bytes>}
                t0 = time.time()
                if data is not None:
                    yield data

    def __iter__(self):

        while True:

            for o in self._iter_frames():
                yield o

            # rtsp-источник иногда вылетает, надо перезапускаться
            if not self.forever:
                break


class FileSender(object):

    def __init__(self, url, **kwargs):
        self.url = url
        self.session = requests.Session()

    def send(self, data, params=None, raise_on_errors=False):
        t0 = time.time()
        r = None
        try:
            r = self.session.post(url=self.url, params=params, files={'data': data})
        except requests.exceptions.ConnectionError:
            raven_client.captureException()
            if raise_on_errors:
                raise
        logger.debug('sent image to %s size %s in %0.2f sec, status=%s',
                     self.url, len(data), time.time() - t0, r and r.status_code or None)


class FileSaver(object):

    def __init__(self, directory):
        self.directory = directory
        os.makedirs(directory, exist_ok=True)
        self.n = 0

    def get_filename(self):
        return os.path.join(self.directory, '{}-{}.jpg'.format(int(time.time()), self.n))

    def save(self, frame):
        self.n += 1
        path = self.get_filename()
        open(path, 'wb').write(frame)
        return path


class RotatingFileSaver(FileSaver):

    def get_filename(self):
        t = int(time.time() / 3600)
        n = self.n % 10
        return os.path.join(self.directory, '{}-{}.jpg'.format(t, n))


def int_or_str(v):
    try:
        return int(v)
    except ValueError:
        return v


def parse_crop(s):
    if not s:
        return None
    return [int(v) for v in s.split('x')]


def run(args):

    t0 = int(time.time())
    n = 0
    reader = ImageReader(path=int_or_str(args['input']),
                         resize_width=args['resize'],
                         rotate=args['rotate'],
                         grayscale=args['grayscale'],
                         sample_rate=args['sample_rate'],
                         forever=args['forever'],
                         crop=parse_crop(args['crop']),
                         current_image_store=RotatingFileSaver('/video/{}'.format(args['camera_id']))
                         )

    sender = FileSender(url=args['url'])

    for data in reader:
        jpeg = data['jpeg']
        frame = data['frame']
        width, height = frame.shape[0], frame.shape[1]
        n += 1
        sender.send(data=jpeg,
                    params={
                        'camera_id': args['camera_id'],
                        'ts': time.time(),
                        'frame_id': '{}.{}'.format(t0, n),
                        'size': '{}x{}'.format(width, height)
                    },
                    raise_on_errors=False)
