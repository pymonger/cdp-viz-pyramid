import logging, simplejson, re, pprint
from urllib2 import urlopen
from urllib import urlencode

from pyramid_handlers import action

from beaker.cache import CacheManager

import cdp_viz.handlers.base as base
import cdp_viz.models as model

log = logging.getLogger(__name__)

class SolrResult(object):
    """Callable class for returning solr results."""
    def __init__(self, ret): self.ret = ret
    def __call__(self):
        #handle jquery 1.3.2 or 1.5.2
        json = re.search(r'^(?:jsonp.*?|jQuery.*?)\((.*)\)$', self.ret).group(1)
        try: return simplejson.loads(json)
        except:
            log.debug("Bad json extracted: %s" % json)
            raise
    
class Solr(base.Handler):
    
    @action(renderer="string")
    def select(self):
        
        log.debug("%s select %s" % ('=' * 30, '=' * 30))
        for param, val in self.request.params.items():
            log.debug("param: %s = %s" % (param, val))
        
        #get cache where entries expire after 30 seconds
        cache = CacheManager().get_cache('solr/select', expire=300)
        
        q = urlencode(self.request.params)
        #log.debug("encoded query is: %s" % q)
        
        #url = 'http://localhost:8983/solr/select?%s'
        
        ret = urlopen('http://localhost:8983/solr/select', q).read()
        
        #use _ value passed by solr-ajax as session id and cache results under it
        sessionId = self.request.params['_']
        cache.get(key=sessionId, createfunc=SolrResult(ret))
        
        #retDict = simplejson.loads(re.search(r'.*?\((.*)\)', ret).group(1))
        #log.debug("ret: %s" % pprint.pformat(retDict))
        
        #return simplejson.loads(ret)
        return ret
    
