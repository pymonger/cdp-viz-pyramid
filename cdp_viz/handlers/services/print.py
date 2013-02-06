import logging, simplejson, pprint, time, os, shutil, httplib2, urllib
from tempfile import mkdtemp
from subprocess import Popen, PIPE

from pyramid_handlers import action

from beaker.cache import CacheManager

import cdp_viz.handlers.base as base
import cdp_viz.models as model

log = logging.getLogger(__name__)

class Print(base.Handler):
    
    @action(renderer="string")
    def index(self):
        http = httplib2.Http('')
        url = self.request.params['url']
        url = urllib.unquote(url)
        (response,content) = http.request(url)
        return content
