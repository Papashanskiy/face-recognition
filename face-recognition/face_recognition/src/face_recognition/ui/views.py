import logging
import os
from django.http import HttpResponse

logger = logging.getLogger(__name__)


class StaticLoader(object):

    def __init__(self, path):
        self.root = path

    def load(self, path):
        fn = os.path.join(self.root, path)
        return open(fn, 'r').read()


static_loader = StaticLoader(path=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static'))


def widget_js(request):
    content = static_loader.load('faces-widget/faces-widget.js')
    return HttpResponse(content=content, status=200, content_type='application/x-javascript; charset=utf-8')

    template = """
     /* Usage:
     
          <script src="https://yastatic.net/jquery/3.1.1/jquery.min.js">
          
          <link href="https://vision-api.invitronet.ru/recognition/ui/faceid/1/widget.css" rel="stylesheet" />
          <script src="https://vision-api.invitronet.ru/recognition/ui/faceid/1/widget.js"></script>
     
         <script type="text/javascript">
         $(document).ready(function(){
                faceid_widget.init('#faceid-widget-placeholder');
          });
          </script>
     */
     
     faceid_widget = {
        init: function (obj, workstation_id) {
            console.debug('faceid_widget.init');
        }
      }
    """
    #return HttpResponse(content=template, status=200, content_type='application/x-javascript')


def widget_css(request):
    content = static_loader.load('faces-widget/faces-widget.css')
    return HttpResponse(content=content, status=200, content_type='text/css; charset=utf-8')
