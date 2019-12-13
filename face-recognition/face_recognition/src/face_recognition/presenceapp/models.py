from django.db import models
import datetime
from django.urls import reverse


class FacePresenceHistoryManager(models.Manager):

    def add_face_presence(self, workstation_id, face_id, time):
        minute_slot = time - datetime.timedelta(seconds=time.second, microseconds=time.microsecond)

        spec = dict(workstation_id=workstation_id, face_id=face_id, minute_slot=minute_slot)
        qs = self.filter(**spec)

        updated = qs.update(seen_times=models.F('seen_times')+1, last_seen_at=time)
        if not updated:
            self.create(**spec)
        return updated

    def has_presence(self, face_id, workstation_id):
        return self.filter(face_id=face_id, workstation_id=workstation_id).count()


class FacePresenceHistory(models.Model):
    face_id = models.BigIntegerField()
    workstation_id = models.CharField(max_length=36)
    minute_slot = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(auto_now=True)
    seen_times = models.SmallIntegerField(default=1)

    objects = FacePresenceHistoryManager()

    class Meta:
        unique_together = (('face_id', 'workstation_id', 'minute_slot'),)
        index_together = (('workstation_id', 'created_at'),)  # индекс по created_at, потому что он реже обновляется

    def as_dict(self, short=True, url=True):
        r = {
            'face_id': self.face_id,
            'last_seen_at': self.last_seen_at
        }

        if url:
            r['face_url'] = '/recognition' + reverse('face-image') + '?id={}'.format(self.face_id) + '&workstation_id={}'.format(self.workstation_id)

        if not short:
            r.update({
                'workstation_id': self.workstation_id,
                'seen_times': self.seen_times,
                'minute_slot': self.minute_slot
            })

        return r


class WorkStationConfig(models.Model):
    workstation_id = models.CharField(max_length=36)
    location_name = models.CharField(max_length=200)
    min_photo_wh = models.PositiveIntegerField()
