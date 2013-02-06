import logging, simplejson, re, os, shutil, pika, time, pprint
from urllib2 import urlopen
from urllib import urlencode
from datetime import datetime
import httplib2
from tempfile import mkdtemp
from subprocess import Popen, PIPE

from pyramid_handlers import action

from beaker.cache import CacheManager

import cdp_viz.handlers.base as base
import cdp_viz.models as model
from cdp_viz.lib.virtuoso import bulk_import_rdf

from solr import indexSession

log = logging.getLogger(__name__)

def uploadAndIndex(provLog):
    """Upload provenance log and index solr documents."""

    #make sure not empty
    if provLog == "": raise RuntimeError("Got empty string for provenance log.")

    headers = {'Content-type': 'application/x-www-form-urlencoded'} # needed for POST
    
    log.debug("TIMING_INFO:%s" % ('#' * 80))
    t1_total = time.time()
    
    #get provenance log as TURTLE
    log.debug("About to get turtle from provenance log")
    t1 = time.time()
    http = httplib2.Http()
    (response, json) = http.request("http://localhost:5000/services/logfile/dump?type=TURTLE", 'POST', 
        provLog, headers)
    t2 = time.time()
    log.debug("TIMING_INFO: REST call to get triples from provenance log took %s seconds." % (t2-t1))
    json = simplejson.loads(json)
    if not json['success']:
        raise RuntimeError("Failed to get triples from provenance log: %s" % json['message'] +
                           "Check provenance log input: %s" % provLog)
    #f = open('/tmp/prov/prov.ttl', 'w')
    #f.write("%s" % json['value'])
    #f.close()
    
    #insert turtle into store using bulk upload method (fastest)
    log.debug("TIMING_INFO:%s" % ('-' * 80))
    log.debug("TIMING_INFO: sessionURI = %s" % json['graphName'])
    log.debug("TIMING_INFO:%s" % ('-' * 80))
    log.debug("About to insert turtle via bulk upload")
    t1 = time.time()
    bulk_import_rdf(json['graphName'], json['value'])
    t2 = time.time()
    log.debug("TIMING_INFO: Bulk insert of triples took %s seconds." % (t2-t1))
    
    #index entities and processes into solr
    log.debug("calling indexSession on graph %s" % json['graphName'])
    t1 = time.time()
    indexSession(json['graphName'])
    t2 = time.time()
    log.debug("TIMING_INFO: indexSession took %s seconds." % (t2-t1))
    t2_total = time.time()
    log.debug("TIMING_INFO: uploadAndIndex took %s seconds." % (t2_total-t1_total))

class Logfile(base.Handler):
    
    @action(renderer="json")
    def upload(self):
        """
        Upload CDP log to Jena store. This is a temporary solution until we can determine why the Jena
        store gets corrupted when populated through the JAX-RS services.
        
        curl -f -v -X POST --data-binary @${PROV_POST} http://cdp-appliance:5001/services/logfile/upload
        """
        
        log.debug("calling upload")
        
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='logfile_upload', durable=True)
        channel.basic_publish(exchange='',
                      routing_key='logfile_upload',
                      body=self.request.body,
                      properties=pika.BasicProperties(
                         delivery_mode = 2, # make message persistent
                      ))
        connection.close()
                      
        log.debug("Sent logfile to logfile_upload rabbitmq queue.")
        return {"success": True}
