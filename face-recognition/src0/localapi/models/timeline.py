import time
from collections import OrderedDict, defaultdict
from datetime import datetime

from core.helpers.datetime import fromtimestamp
from .faces import imagedb, get_master_object


class SlotData(object):
    def __init__(self):
        self.name = None
        self.time = None
        self.faces = []
        self.masters = OrderedDict()


class FaceMasterData(object):
    def __init__(self, master_id):
        self.master = get_master_object(id=master_id)
        self.faces = []

    def last_faces(self, limit=3):
        return self.faces[:limit]


class Timeline(object):

    def __init__(self, limit_minutes=24*60, show_hidden=False):
        self.limit_minutes = limit_minutes
        self.show_hidden = show_hidden

    def group_masters(self, faces):
        r = OrderedDict()
        for o in faces:
            master_id = o.get('master')
            if not master_id:
                continue
            if master_id not in r:
                master_data = FaceMasterData(master_id=master_id)
                if master_data.master.get('hide'):
                    # Не показывать скрытые мастера
                    continue
                r[master_id] = master_data
            else:
                master_data = r[master_id]
            master_data.faces.append(o)
        return r.values()

    def iter_slots(self):
        """
        Основная функция. Читает всё из базы и возвращает список SlotData
        :return:
        """
        slots = defaultdict(SlotData)
        spec = {'t': {'$gt': time.time() - self.limit_minutes*60}}
        for o in imagedb.collection.find(spec, {'t': 1, '_id': 1, 'master': 1}, sort=[('t', -1)], limit=100000):
            t = fromtimestamp(o['t'])
            slot_time = datetime(year=t.year, month=t.month, day=t.day, hour=t.hour, minute=int(t.minute / 10)*10)
            slot_name = slot_time.strftime('%Y-%m-%d-%H-%M')
            data = slots[slot_name]
            data.time = slot_time
            data.name = slot_name
            data.faces.append(o)

        for key in sorted(slots.keys())[::-1]:
            slot = slots[key]
            slot.masters = self.group_masters(slot.faces)
            yield slot

