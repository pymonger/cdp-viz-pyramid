import logging, simplejson, re, pprint, time, os, shutil
from urllib2 import urlopen
from urllib import urlencode
from datetime import datetime
import httplib2
from tempfile import mkdtemp
from subprocess import Popen, PIPE

from pysolr.Solr import Solr as pysolr_solr
from pysolr.SolrException import SolrException
from pysolrprov.PROVSPARQL import PROVSPARQL

from pyramid_handlers import action

from beaker.cache import CacheManager

import cdp_viz.handlers.base as base
import cdp_viz.models as model

log = logging.getLogger(__name__)

josekiURL = "http://localhost:2020/sparql"
queryURL = "http://localhost:5000/services/cdp_jena/query"
queryURL2 = "http://localhost:5001/services/rdf/query"
queryURL3 = "http://localhost:8890/sparql"
solrURL = "http://localhost:8983"
wadlURL = "http://localhost:5000"

COMMIT_THRESHOLD = 500

def indexSession(graphName):
    """Index entities and processes from a session graphName."""
    
    http = httplib2.Http()
    solr = pysolr_solr(http, solrURL)
    prov = PROVSPARQL(http, queryURL3, wadlURL, graphName)
    
    t1 = time.time()
    entities = prov.getEntityDocs()
    t2 = time.time()
    log.debug("TIMING_INFO: prov.getEntityDocs() took %s seconds to get %d entities." % (t2-t1, len(entities)))
    
    docCount = 0
    t1_docs = time.time()
    docs = []
    for entityURI in entities:
        log.debug('----------------%s -----------------' % entityURI)
        
        #skip if URI doesn't provide timestamp
        #if entityURI.endswith('unknown'): continue
        #else: docCount += 1
        docCount += 1
        
        docs.append(entities[entityURI])
        #pprint.pprint(entities[entityURI])
        
        if docCount % COMMIT_THRESHOLD == 0:
            try:
                t1 = time.time()
                (response, content) = solr.addMultiple(docs)
                (response, content) = solr.commit()
                t2 = time.time()
                log.debug("solr.update() took %s seconds." % (t2-t1))
                log.debug('response: %s' % str(response) )
                log.debug('content: %s' % str(content) )
                log.debug('http status: %s' % response.status)
                solrResponseHeader = content['responseHeader']
                log.debug('solr status: %s' % solrResponseHeader['status'])
            except SolrException, e:
                log.warning('unable to make request to solr: %s' % str(e) )
            except Exception, e:
                log.warning('unable to make request to solr: %s' % str(e) )
            docs = []
    
    try:
        t1 = time.time()
        (response, content) = solr.addMultiple(docs)
        (response, content) = solr.commit()
        t2 = time.time()
        log.debug("solr.update() took %s seconds." % (t2-t1))
        log.debug('response: %s' % str(response) )
        log.debug('content: %s' % str(content) )
        log.debug('http status: %s' % response.status)
        solrResponseHeader = content['responseHeader']
        log.debug('solr status: %s' % solrResponseHeader['status'])
    except SolrException, e:
        log.warning('unable to make request to solr: %s' % str(e) )
    except Exception, e:
        log.warning('unable to make request to solr: %s' % str(e) )
        
    t2_docs = time.time()
    log.debug("TIMING_INFO: SOLR add & commit of %d entities took %s seconds." % (len(entities), t2_docs-t1_docs))

    t1 = time.time()
    processes = prov.getProcessDocs()
    t2 = time.time()
    log.debug("TIMING_INFO: prov.getProcessDocs() took %s seconds to get %d processes." % (t2-t1, len(processes)))
    docCount = 0
    docs = []
    t1_docs = time.time()
    for processURI in processes:
        log.debug('----------------%s -----------------' % processURI)
        
        #skip if URI doesn't provide timestamp
        if processURI.endswith('unknown'): continue
        else: docCount += 1
        
        docs.append(processes[processURI])
        
        if docCount % COMMIT_THRESHOLD == 0:
            try:
                t1 = time.time()
                (response, content) = solr.addMultiple(docs)
                (response, content) = solr.commit()
                t2 = time.time()
                log.debug("solr.update() took %s seconds." % (t2-t1))
                log.debug('response: %s' % str(response) )
                log.debug('content: %s' % str(content) )
                log.debug('http status: %s' % response.status)
                solrResponseHeader = content['responseHeader']
                log.debug('solr status: %s' % solrResponseHeader['status'])
            except SolrException, e:
                log.warning('unable to make request to solr: %s' % str(e) )
            except Exception, e:
                log.warning('unable to make request to solr: %s' % str(e) )
            docs = []
    
    try:
        t1 = time.time()
        (response, content) = solr.addMultiple(docs)
        (response, content) = solr.commit()
        t2 = time.time()
        log.debug("solr.update() took %s seconds." % (t2-t1))
        log.debug('response: %s' % str(response) )
        log.debug('content: %s' % str(content) )
        log.debug('http status: %s' % response.status)
        solrResponseHeader = content['responseHeader']
        log.debug('solr status: %s' % solrResponseHeader['status'])
    except SolrException, e:
        log.warning('unable to make request to solr: %s' % str(e) )
    except Exception, e:
        log.warning('unable to make request to solr: %s' % str(e) )
    
    t2_docs = time.time()
    log.debug("TIMING_INFO: SOLR add & commit of %d processes took %s seconds." % (len(processes), t2_docs-t1_docs))
    
class Solr(base.Handler):
    
    @action(renderer="json")
    def index_session(self):
        
        log.debug("%s select %s" % ('=' * 30, '=' * 30))
        for param, val in self.request.params.items():
            log.debug("param: %s = %s" % (param, val))

        graphName = self.request.params['graphName']
        indexSession(graphName)
        
        return {'success': True}
