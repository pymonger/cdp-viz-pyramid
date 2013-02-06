import simplejson, httplib2, logging
from urllib import urlencode, urlopen

from pysolrprov.PROVSPARQL import (ENTITIES_SPARQL, ENTITIES_BY_NAMEDGRAPH_SPARQL_TMPL,
SESSION_SPARQL_TMPL, SESSION_BY_ENTITY_MD5_SPARQL_TMPL, MD5_SPARQL_TMPL, 
MANIFEST_SPARQL_TMPL, LANDING_PAGE_SPARQL_TMPL)

log = logging.getLogger(__name__)

#JOSEKI_URL = "http://localhost:2020/sparql?output=json&%s"
#ARQ_URL = "http://localhost:5000/services/cdp_jena/query"
SPARQL_ENDPOINT = "http://localhost:8890/sparql"

def sparqlQuery(sparql):
    """Make REST call to SPARQL endpoint."""
    
    data = {'format': 'application/sparql-results+json', 
            'query': sparql}
    #logger.debug('data=%s' % data)
    headers = {'Content-type': 'application/x-www-form-urlencoded'} # needed for POST
    body = urlencode(data)
    (response, content) = httplib2.Http().request(SPARQL_ENDPOINT, 'POST', body, headers)
    #f = open('/tmp/sparql.txt', 'w')
    #f.write(body)
    #f.close()
    jsonResults = simplejson.loads(content)
    if 'arqResults' in jsonResults: arqResults = jsonResults['arqResults']
    else: arqResults = jsonResults
    return simplejson.dumps(arqResults)
