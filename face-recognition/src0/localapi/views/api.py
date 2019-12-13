import hug

from io import BytesIO
from localapi.models.faces import (get_master_object, get_faces_data, get_images_for_master, masterdb, imagedb)


@hug.get('/faces.json')
def get_faces(last_seconds: int=None, count: int=None, filter: str=None, output=hug.output_format.json):
    return {'faces': get_faces_data(last_seconds=last_seconds, limit=count or 10, filter=filter)}


@hug.post('/face-link-to-subject.json')
def face_edit_save_json(id, subject_id, output=hug.output_format.json):
    master = get_master_object(id=id)
    master['subject_id'] = subject_id
    masterdb.collection.save(master)
    return {
        'status': 'ok',
        'id': id,
        'subject_id': subject_id
    }


@hug.post('/face-save')
def face_edit_save(id, subject_id):
    master = get_master_object(id=id)
    master['subject_id'] = subject_id
    masterdb.collection.save(master)
    return hug.redirect.to('/faces.html')


@hug.post('/face-hide.json')
def face_hide_json(id):
    master = get_master_object(id=id)
    master['hide'] = True
    masterdb.collection.save(master)
    return {
        'status': 'ok',
        'id': id
    }


@hug.post('/face-hide')
def face_hide(id):
    master = get_master_object(id=id)
    master['hide'] = True
    masterdb.collection.save(master)
    return hug.redirect.to('/faces.html')


@hug.post('/face-link')
def face_link_save(id, subject_id):
    master = get_master_object(id=id)
    master['subject_id'] = subject_id
    masterdb.collection.save(master)
    return True


@hug.get('/images')
@hug.cli()
def get_images_for_face(faceid:hug.types.text, output=hug.output_format.json):
    r = get_images_for_master(master_id=faceid, limit=10, url='/images/{}.jpg')
    return {'images': r}


def load_image_by_id(id, debug=False):
    o = imagedb.load(id=id)
    if debug:
        img = o.get('debug_img') or o.get('image')
    else:
        img = o['image']
    return bytes(img)


@hug.get('/images/{image_id}.jpg', output=hug.output_format.jpeg_image)
def get_image(image_id, response, debug=False, output=hug.output_format.jpeg_image):
    # print('response', type(response), dir(response))
    response.cache_control = ['public', 'max-age=144000']
    return BytesIO(load_image_by_id(id=image_id, debug=debug))


@hug.get('/image-by-subject/{subject_id}.jpg', output=hug.output_format.jpeg_image)
def get_subject_image(subject_id, response, debug=False):
    response.cache_control = ['public', 'max-age=144000']
    response.cache_control = ['public', 'max-age=144000']
    o = masterdb.get_by_subject_id(subject_id=subject_id)
    image_id = str(o['_id'])
    return BytesIO(load_image_by_id(id=image_id, debug=debug))
