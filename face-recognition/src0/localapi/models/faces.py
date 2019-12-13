import core.db
from core.helpers.datetime import now, to_local_time
from datetime import timedelta
from bson.objectid import ObjectId
import logging

masterdb = core.db.ImageMaster()
imagedb = core.db.Image()


def face_data(o, load_images=20):
    r = {'id': str(o['_id']),
            'last_seen': to_local_time(o['last_seen']),
            'subject_id': o.get('subject_id'),
            'merged_cnt': o.get('merged_cnt'),
            'image': '/images/{}.jpg'.format(o['_id']),
            'images': ['/images/{}.jpg'.format(o['_id'])],
            }

    if load_images:
        images = get_images_for_master(master_id=o['_id'], limit=load_images)
        if images:
            r['images'] = images

    return r


def get_master_object(id):
    spec = {'_id': ObjectId(id)}
    for o in masterdb.collection.find(spec):
        return o


def get_masters(seconds=100*60, merged_cnt=1, limit=100, filter=None):
    spec = {'last_seen': {'$gt': now() - timedelta(seconds=seconds)},
            'merged_cnt': {'$gt': merged_cnt},
            'hide': {'$ne': True}}
    if filter == 'recognized':
        spec['subject_id'] = {'$ne': None}
    elif filter == 'nonrecognized':
        spec['subject_id'] = None
    elif filter:
        logging.warning('get_masters: unknown filter value %s', filter)
    logging.debug('get_masters spec=%s', spec)
    return masterdb.collection.find(spec, sort=[('last_seen', -1), ('merged_cnt', -1), ], limit=limit)


def get_faces_data(load_images=20, limit=20, last_seconds=None, filter=None):
    r = []
    for o in get_masters(seconds=last_seconds or 240*60, limit=limit or 20, filter=filter):
        r.append(face_data(o, load_images=load_images or 1))
    return r


def get_images_for_master(master_id, limit=7, url='/images/{}.jpg'):
    r = []
    spec = {'master': ObjectId(master_id)}
    for o in imagedb.collection.find(spec, sort=[('t', -1)], limit=limit):
        r.append({'id': str(o['_id']),
                  't': o['t'],
                  'src': url.format(o['_id'])
                  })
    return r
