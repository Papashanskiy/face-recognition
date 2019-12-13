from django.core.management.base import BaseCommand, CommandError
from face_recognition.recognitionapp.models import FacePhoto
from PIL import Image
import io


class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        # parser.add_argument('poll_id', nargs='+', type=int)
        pass

    def handle(self, *args, **options):
        for o in FacePhoto.objects.filter(wh=None):
            img = Image.open(io.BytesIO(o.image_blob))
            o.wh = img.width * img.height
            o.save()
            self.stdout.write(self.style.SUCCESS('Updated {} {}'.format(o.id, o.wh)))
