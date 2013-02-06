import logging, simplejson, pprint, time, os, shutil, httplib2, urllib
from tempfile import mkdtemp
from subprocess import Popen, PIPE

from pyramid_handlers import action

from beaker.cache import CacheManager

import cdp_viz.handlers.base as base
import cdp_viz.models as model

log = logging.getLogger(__name__)

class Rdf(base.Handler):
    
    @action(renderer="json")
    def query(self):
        """
        SPARQL query store:
        curl -v -X POST --data-ascii @test.sparql http://localhost:5001/services/rdf/query
        """
        
        headers = {'Content-type': 'application/x-www-form-urlencoded'} # needed for POST
        http = httplib2.Http('.cache')
        params = urllib.urlencode({
            'format': 'application/sparql-results+json',
            'query': self.request.body
        })
        (response,json) = http.request("http://localhost:8890/sparql", 'POST', params, headers)
        
        return simplejson.loads(json)
    
    @action(renderer="json")
    def query_triples(self):
        
        arqResults = self.query()
        
        #make sure this result set is for triples
        vars = arqResults['head']['vars']
        if len(vars) != 3:
            raise RuntimeError("SPARQL query neds to return triples. Detected only %d variables returned." % \
                               len(vars))
            
        #build triples
        triples = ""
        bindings = arqResults['results']['bindings']
        for binding in bindings:
            for v in vars:
                b = binding[v]
                t = b['type']
                val = b['value']
                if t == "uri": triples += "<%s> " % val
                elif t == "typed-literal": triples += '"%s"^^<%s>' % (val, b['datatype'])
                else: triples += "%s " % val
            triples += ".\n"
        
        return {
            'status': 'success',
            'message': '',
            'triples': triples
        }
