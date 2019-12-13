import datetime
import json
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class RecognizeImage(object):
    def __init__(self, data, name=None, person_id=None):
        self.data = data
        self.name = name
        self.person_id = person_id


class VisionAPIBaseResponse(object):

    def __init__(self, response, parent):
        self.body = response.json()['body']
        self.response = response
        self.parent = parent


class VisionAPIBase(object):
    """
    Документация
        1. Добавить человека https://help.mail.ru/biz/vision/api/v1/persons/set
        2. Удалить человека https://help.mail.ru/biz/vision/api/v1/persons/delete
        3. Найти по залитой базе https://help.mail.ru/biz/vision/api/v1/persons/recognize
        4. Получение токена https://help.mail.ru/biz/vision/api/v1/oauth_token
    """

    response_cls = VisionAPIBaseResponse
    oauth_provider = 'mcs'

    def __init__(self, client_id=None, client_secret=None, service_token=None, space='0'):
        self.client_secret = client_secret
        self.client_id = client_id
        self.token = service_token

        assert (self.client_secret and self.client_id) or self.token

        self.session = requests.Session()
        self.token_expires_at = None
        self.space = space

    def auth(self, force=False):

        now = datetime.datetime.now()

        if self.token:
            if self.token_expires_at:
                if now >= self.token_expires_at:
                    self.token = None

        if self.token is None or force:
            r = self.session.post(url='https://o2.mail.ru/token', data={'client_id': self.client_id,
                                                                        'client_secret': self.client_secret,
                                                                        'grant_type': 'client_credentials'})
            r.raise_for_status()
            resp = r.json()
            logger.debug('auth results: %s', resp)
            self.token = resp['access_token']
            self.token_expires_at = now + datetime.timedelta(seconds=resp['expires_in'] - 10)

    def recognize_many(self, images, space=None, create_new=False):
        self.auth()
        space = space or self.space
        if not isinstance(images, (list, tuple)):
            images = [images, ]

        files = {}
        names = []

        for image in images:
            # files[image.name] = image.data
            files[image.name] = (image.name, image.data, 'image/jpeg')
            d = {'name': image.name}
            if image.person_id:
                d['person_id'] = image.person_id
            names.append(d)

        r = self.session.post(
            url='https://smarty.mail.ru/api/v1/persons/recognize',
            # url='http://requestbin.fullcontact.com/175gnq11',
            params={'oauth_token': self.token, 'oauth_provider': self.oauth_provider},
            files=files,
            data={'meta': json.dumps({'space': space, 'create_new': create_new, 'images': names})})

        r.raise_for_status()
        return self.response_cls(response=r, parent=self)

    def recognize_one(self, image, space='0', create_new=False):
        return self.recognize_many(images=[image, ], space=space, create_new=create_new)


class VisionAPI(VisionAPIBase):

    def __init__(self):
        super(VisionAPI, self).__init__(
            #client_id=settings.MAILRU_CLIENT_ID,
            #client_secret=settings.MAILRU_CLIENT_SECRET,
            service_token=settings.MAILRU_SERVICE_TOKEN
        )


class RecognizedPerson(object):

    def __init__(self, person, provider):
        self.coord = person['coord']
        self.confidence = person['confidence']
        self.awesomeness = person['awesomeness']
        self.person_id = person['tag']
        self.tag = self.person_id
        self.provider = provider

    def get_global_id(self):
        return "{}:{}:{}".format(self.provider.client_id, self.provider.space, self.tag)

    @classmethod
    def from_response(cls, response):
        r = []
        try:
            objects = response.body.get('objects', [])
        except AttributeError:
            logger.exception('Error in body: %s', response.body)
            raise

        for o in objects:
            for person in o.get('persons', []):
                r.append(cls(person, provider=response.parent))
        return r
