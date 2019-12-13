import hug

from io import BytesIO
from localapi.models.faces import (
    face_data, get_master_object, get_masters, get_faces_data, get_images_for_master, masterdb, imagedb)
from localapi.models.timeline import Timeline
from core.db import UIPatients
import json
import os

this_dir = os.path.dirname(os.path.abspath(__file__))


@hug.get('/favicon.ico')
def favicon_ico():
    return {}


template_engine = None


def get_template(name):

    global template_engine

    if template_engine is None:
        import os
        from jinja2 import FileSystemLoader, Environment
        template_root = os.path.join(this_dir, '../templates')
        template_engine = Environment(loader=FileSystemLoader(template_root))

    return template_engine.get_template(name)


@hug.get('/', output=hug.output_format.html)
def index_html():
    template = get_template("index.html")
    return template.render()


@hug.get('/dashboard/index.html', output=hug.output_format.html)
def dashboard_index_html():
    template = get_template("dashboard/index.html")
    return template.render()


@hug.get('/dashboard/patients.html', output=hug.output_format.html)
def dashboard_index_html():
    template = get_template("dashboard/patients.html")
    return template.render()


@hug.get('/dashboard/patientcard.html', output=hug.output_format.html)
def dashboard_index_html():
    template = get_template("dashboard/patientcard.html")
    return template.render()


@hug.get('/dashboard/cart.html', output=hug.output_format.html)
def dashboard_index_html():
    template = get_template("dashboard/cart.html")
    return template.render()


@hug.get('/dashboard/camera.html', output=hug.output_format.html)
def dashboard_index_html():
    template = get_template("dashboard/camera.html")
    return template.render()


@hug.get('/dashboard/incomers.html', output=hug.output_format.html)
def incomers_html():
    template = get_template("dashboard/incomers.html")
    return template.render()


@hug.get('/prototype/non-marked.html', output=hug.output_format.html)
def incomers_html():
    template = get_template("prototype/non-marked.html")
    return template.render()

@hug.get('/prototype/marked.html', output=hug.output_format.html)
def prototype_marked_html():
    template = get_template("prototype/marked.html")
    return template.render()

@hug.get('/names.html', output=hug.output_format.html)
def names_html():
    template = get_template("names.html")
    names = [face_data(o, load_images=0) for o in get_masters(minutes=1000)]
    return template.render(names=names)


@hug.get('/timeline.html', output=hug.output_format.html)
def timeline_html():
    template = get_template("timeline.html")
    timeline = Timeline(limit_minutes=60*3)
    return template.render(timeline=timeline)


@hug.get('/realtime.html', output=hug.output_format.html)
def timeline_html():
    template = get_template("realtime.html")
    return template.render()


@hug.get('/faces.html', output=hug.output_format.html)
def faces_html():
    template = get_template("faces.html")
    faces = get_faces_data(load_images=20)
    return template.render(faces=faces)


@hug.get('/face-edit.html', output=hug.output_format.html)
def face_edit_html(id):
    template = get_template("face-edit.html")
    master = get_master_object(id=id)
    data = face_data(master, load_images=20)
    return template.render(face=data)


@hug.static('/static')
def static_dirs():
    return [os.path.join(this_dir, '../templates/static/')]


@hug.static('/js')
def js_dirs():
    return [os.path.join(this_dir, '../templates/js/')]


@hug.get('/current-image.jpg', output=hug.output_format.jpeg_image)
def get_current_image(response):
    from core.db import LocalFilestore
    return BytesIO(LocalFilestore().read())


@hug.get('/current-image-debug.jpg', output=hug.output_format.jpeg_image)
def get_current_image(response):
    from core.db import DebugImageFilestore
    return BytesIO(DebugImageFilestore().read())


# ---------  Ручки для работы с пациентами

@hug.get('/patients/list.json')
def get_patients_list():
    items = list(UIPatients().get_list())
    # items = [{'_id': 'X'}, {'_id': 'Y'}]
    return {'items': items}


@hug.get('/patients/get.json', output=hug.output_format.text)
def get_patient(id: str, response, callback: str=None):
    #
    # hug - удивительная штука, сначала 'вау', потом оказывается редкостным говнищем
    #
    ret = {'item': UIPatients().get(id=id)}
    if callback:
        response.content_type = 'application/javascript'
        return "{}({})".format(callback, json.dumps(ret))
    else:
        response.content_type = 'application/json'
        return json.dumps(ret)


@hug.post('/patients/add.json')
def add_patient(body):
    return {'status': 'ok', 'id': str(UIPatients().insert(data=body))}


@hug.post('/patients/edit.json')
def edit_patient(body):
    id = body.get('id')
    if not id:
        id = str(UIPatients().insert(data=body))
    else:
        UIPatients().update(id=id, data=body)
    if body.get('link_with_face_id'):
        # Привяжем лицо к карточке
        masterdb.set_subject_id(id=body.get('link_with_face_id'), subject_id=id)
    return {'status': 'ok'}


@hug.post('/patients/delete.json')
def delete_patient():
    return {'status': 'ok'}
