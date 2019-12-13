import pymongo
from bson.objectid import ObjectId
import time
import settings
import logging

from core.helpers.datetime import now
import operator

from scipy.spatial import distance
import random

logger = logging.getLogger(__name__)


class MongodbStore(object):

    DATABASE_NAME = None

    def __init__(self, mongodb_connection=None, db=None):
        self.client = pymongo.MongoClient(mongodb_connection or settings.MONGODB_CONNECTION,
                                          w=1, connect=False)  # connect=False важно для celery
        self.db = self.client[db or self.DATABASE_NAME]

    def get_collection(self, name):
        return self.db[name]


class Image(MongodbStore):

    DATABASE_NAME = 'faces'

    def __init__(self):
        super(Image, self).__init__()
        self.collection = self.get_collection('images')

    def save(self, img):
        o = self.collection.insert_one({'image': img, 't': int(time.time())}).inserted_id
        return o

    def add_debug_image(self, id, img, shape=None):
        self.collection.update_one({'_id': ObjectId(id)}, {'$set': {'debug_img': img, 'shape': shape}})

    def load(self, id):
        return self.collection.find_one({'_id': ObjectId(id)})

    def delete(self, id):
        return self.collection.delete_one({'_id': ObjectId(id)})

    def set_master(self, id, master_id):
        self.collection.find_one_and_update({'_id': ObjectId(id)},
                                            {'$set': {'master': ObjectId(master_id)}})

    def __iter__(self):
        for obj in self.collection.find():
            yield obj


class UIPatients(MongodbStore):

    DATABASE_NAME = 'ui_patients'

    def __init__(self):
        super(UIPatients, self).__init__()
        self.patients_collection = self.get_collection('patients')

    def get_list(self):
        for o in self.patients_collection.find().sort('name', 1):
            o['id'] = str(o.pop('_id'))
            yield o

    def get(self, id):
        try:
            id = ObjectId(id)
        except:
            pass
        o = self.patients_collection.find_one({'_id': id})
        o['id'] = str(o.pop('_id'))
        return o

    def update(self, id, data, upsert=True):
        try:
            id = ObjectId(id)
        except:
            pass
        result = self.patients_collection.replace_one({'_id': id}, data, upsert=upsert)
        return result.upserted_id

    def insert(self, data, update=True):
        id = '{} {}'.format(data['name'], data['surname'])
        data['_id'] = id
        if 'revenue' not in data:
            data['revenue'] = random.randint(9, 140) * 100
        if 'email' not in data:
            data['email'] = "{}@mail.ru".format(random.randint(100000, 999999))
        if 'city' not in data:
            data['city'] = random.choice(['Москва', 'Санкт-Петербург', 'Владивосток'])
        if 'address' not in data:
            data['address'] = "{}, {}".format(random.choice(['Нагатинская', 'Ленина', 'Комсомольский проспект', 'Мира', 'Горького']), random.randint(1,100))

        if update:
            self.patients_collection.replace_one({'_id': id}, data, upsert=True)
            return id
        else:
            return self.patients_collection.insert_one(data, upsert=True).inserted_id

    def delete(self, id):
        return self.patients_collection.delete_one({'_id': ObjectId(id)})


class ImageDescriptor(MongodbStore):

    DATABASE_NAME = 'faces'

    def __init__(self):
        super(ImageDescriptor, self).__init__()
        self.collection = self.get_collection('fd')

    def save(self, image_id, descriptor):
        logger.debug("FaceDescriptor.save %s %s", image_id, descriptor)
        o = self.collection.insert({'_id': ObjectId(image_id), 'd': descriptor})
        return o

    def load(self, id):
        return self.collection.find_one({'_id': ObjectId(id)})

    def set_master(self, id, master_id):
        self.collection.find_one_and_update({'_id': ObjectId(id)},
                                            {'$set': {'master': ObjectId(master_id)}})


class ImageMaster(MongodbStore):

    """
    _id: <id>,
    last_seen: <datetime>,
    created_at: <datetime>,
    d: [...],  // vector descriptor
    subject_id: null,
    """

    DATABASE_NAME = 'faces'

    def __init__(self):
        super(ImageMaster, self).__init__()
        self.collection = self.get_collection('masters')

    def new(self, image_id, descriptor):
        logger.debug("ImageMaster.new %s", descriptor)
        o = self.collection.insert_one({'_id': ObjectId(image_id), 'd': descriptor, 't': time.time()}).inserted_id
        return o

    def set_hide(self, image_id):
        self.collection.find_one_and_update({'_id': ObjectId(image_id)}, {'$set': {'hide': True}})

    def find_nearest_id(self, descriptor, max_distance=0.6, max_found=1000):
        nearest = []
        found = 0
        for o in self.collection.find():
            d = distance.euclidean(descriptor, o['d'])
            if d < max_distance:
                nearest.append([o['_id'], d])
                found += 1
                if found > max_found:
                    break

        if nearest:
            nearest = sorted(nearest, key=operator.itemgetter(1))
            return nearest[0][0]

    def set_subject_id(self, id, subject_id):
        self.collection.find_one_and_update({'_id': ObjectId(id)}, {'$set': {'subject_id': subject_id}})

    def get_by_subject_id(self, subject_id):
        return self.collection.find_one({'subject_id': subject_id})

    def merge_or_create(self, image_id, descriptor, max_distance=0.6):
        nearest_id = self.find_nearest_id(descriptor, max_distance=max_distance)
        if nearest_id:
            created = False
            self.collection.find_one_and_update({'_id': ObjectId(nearest_id)},
                                                {'$set': {'last_seen': now()},
                                                 '$inc': {'merged_cnt': 1}})
        else:
            nearest_id = self.collection.insert_one({'_id': ObjectId(image_id),
                                                     'd': descriptor,
                                                     'last_seen': now(),
                                                     'first_seen': now()}).inserted_id
            created = True
        return nearest_id, created

    def load(self, id):
        return self.collection.find_one({'_id': ObjectId(id)})


class LocalFilestore(object):
    """
    Класс для хранения одной картинки - текущей картинки от камеры
    """

    def __init__(self, path='/tmp/current.jpg', enabled=True):
        self.path = path
        self.enabled = enabled

    def save(self, data):
        if not self.enabled:
            return

        if self.path:
            with open(self.path, 'wb') as f:
                f.write(data)

    def get_path(self):
        return self.path

    def read(self):
        with open(self.path, 'rb') as f:
            return f.read()


class DebugImageFilestore(LocalFilestore):

    def __init__(self, path='/tmp/current-debug.jpg'):
        super(DebugImageFilestore, self).__init__(path=path)
