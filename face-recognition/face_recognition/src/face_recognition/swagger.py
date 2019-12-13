from django.views.generic.base import View, HttpResponse
import os

class SwaggerJsonView(View):

    def get(self, request, *args):
        THIS_DIR = os.path.abspath(os.path.dirname(__file__))
        content = open(os.path.join(THIS_DIR, 'swagger.json'), 'r').read()
        return HttpResponse(content=content, content_type='application/json')
