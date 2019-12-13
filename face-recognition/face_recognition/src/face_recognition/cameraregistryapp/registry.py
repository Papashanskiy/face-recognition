import logging
from django.conf import settings
from face_recognition.recognitionapp import developer_workstations

WORKSTATIONID_TO_CAMERA = None


logger = logging.getLogger(__name__)

def get_camera_by_workstation_id(workstation_id):
    global WORKSTATIONID_TO_CAMERA
    if WORKSTATIONID_TO_CAMERA is None:
        WORKSTATIONID_TO_CAMERA = {}
        for camera_id, data in settings.CAMERAID_TO_WORKSTATION.items():
            data['camera_id'] = camera_id
            WORKSTATIONID_TO_CAMERA[data['workstation_id']] = data

        # Добавляем девелоперские рабочие станции
        for k, v in developer_workstations.MAPPING.items():
            if k not in WORKSTATIONID_TO_CAMERA:
                WORKSTATIONID_TO_CAMERA[k] = WORKSTATIONID_TO_CAMERA.get(v)

    return WORKSTATIONID_TO_CAMERA.get(workstation_id, None)


def get_camera_id_by_workstation_id(workstation_id, default=None):
    o = get_camera_by_workstation_id(workstation_id)
    if o:
        return o.get('camera_id', default)
    else:
        logger.warn('unknown workstation_id: %s', workstation_id)
        return default


def get_camera_by_id(camera_id):
    return settings.CAMERAID_TO_WORKSTATION[camera_id]

