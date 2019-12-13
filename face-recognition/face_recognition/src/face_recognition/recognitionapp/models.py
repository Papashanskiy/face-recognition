from django.db import models


class Face(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(auto_now_add=True)


class FacePhoto(models.Model):
    face = models.ForeignKey(to=Face, db_constraint=False, db_index=True, on_delete=models.DO_NOTHING)
    image_blob = models.BinaryField(help_text='jpeg image')  # TODO: перенести в облако ?
    wh = models.IntegerField(null=True, help_text='Площадь изображения в пикселях, для фильтрации мелких картинок')
    awesomeness = models.DecimalField(max_digits=6, decimal_places=5)
    workstation_id = models.CharField(max_length=36, help_text='С какой камеры/рабочего места это фото', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def as_dict(self, url=False):
        r = {
            'face_id': self.face.id,
            'id': self.id,
            'awesomeness': self.awesomeness,
            'created_at': self.created_at,
            'modified_at': self.modified_at,
            'wh': self.wh
        }
        return r


class ProviderIdManager(models.Manager):

    def set_id(self, face_id, provider, provider_id):
        o, created = self.get_or_create(provider=provider, face_id=face_id, defaults={'inner_id': provider_id})
        if not created:
            if o.inner_id != provider_id:
                self.filter(provider=provider, face_id=face_id).update(inner_id=provider_id)
                created = True
        return o, created


class ProviderId(models.Model):

    class Provider:
        ARM_GUID = 1
        MAILRU_VISION = 100

    objects = ProviderIdManager()

    face = models.ForeignKey(to=Face, db_constraint=False, db_index=True, on_delete=models.DO_NOTHING)
    provider = models.SmallIntegerField(choices=[(Provider.ARM_GUID, 'arm guid'),
                                                 (Provider.MAILRU_VISION, 'mailru vision')],
                                        null=True)
    inner_id = models.CharField(max_length=64, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
