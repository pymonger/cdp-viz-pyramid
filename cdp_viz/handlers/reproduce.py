import logging, simplejson, pprint, re, os, sys, boto, socket, httplib2, time
from urllib2 import urlopen
from urllib import urlencode, unquote

from pyramid_handlers import action

from beaker.cache import CacheManager

import cdp_viz.handlers.base as base
import cdp_viz.models as model

log = logging.getLogger(__name__)


class Reproduce(base.Handler):
    @action(renderer='json')
    def startInstance(self):

        # credentials
        ACCESS_KEY_ID = 'AKIAIT54DZAHF4XT3Y2Q'
        SECRET_ACCESS_KEY = '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'
        
        # AMI and instance info
        ami_id = 'ami-ed2b9a84'
        instance_type = 'c1.medium'
        #instance_type = 't1.micro'
        #instance_type = 'm1.large'
        key_name = 'gmaniponkey'
        security_groups = ['sciflo']

        #get connection to EC2
        conn = boto.connect_ec2(ACCESS_KEY_ID, SECRET_ACCESS_KEY)

        #check if there is already an instance that is up
        filters = {
            'key-name' : key_name,
            'instance-state-name' : 'running',
            'group-name': 'sciflo',
            'image-id': ami_id,
        }
        reservations = conn.get_all_instances(filters=filters)
        instances = [i for r in reservations for i in r.instances]
        if len(instances) == 0:
            # start up instance
            res = conn.run_instances(ami_id, key_name=key_name,
                                     instance_type=instance_type,
                                     instance_initiated_shutdown_behavior="terminate",
                                     security_groups=security_groups)
            inst = res.instances[0]
        else:
            # use existing instance
            inst = instances[0]
            
        
        # wait until status is running
        while True:
            try: inst.update()
            except:
                time.sleep(5)
                continue
            if inst.state == 'running': break
            time.sleep(5)
        
        # get urls
        flowUrl = "%shash=%s&filename=%s" % (self.request.params['dlLink'],
                                             self.request.params['hash'],
                                             self.request.params['filename'])
        query_args = {'flow': urlopen(flowUrl).read(),
                      'filename': self.request.params['filename']}
        enc_args = urlencode(query_args)
        url = "http://%s/wsgi/cvo" % inst.public_dns_name
        uploadUrl = url + '/services/uploadFlow'
        
        # wait until service is running
        con = httplib2.Http(timeout=5)
        while True:
            try:
                resp, cont = con.request(uploadUrl, "GET")
                break
            #except socket.timeout: pass
            #except socket.error: pass
            except Exception, e:
                print >>sys.stderr, str(e)
        
        # upload sciflo to EC2 instance
        log.debug(uploadUrl)
        log.debug(urlopen(uploadUrl, enc_args).read())
        
        # sciflo execution page
        sflExecUrl = "http://%s/sciflo/cgi-bin/submit_sciflo.cgi?scifloStr=/wsgi/cvo/flows/%s" % (inst.public_dns_name, self.request.params['filename'])
        log.debug("Check at %s" % sflExecUrl)
        return {"url": sflExecUrl}

    @action(renderer="reproduce.mako")
    def index(self):
        return {
            "title": "Reproduce",
            "dlLink": self.request.params['dlLink'],
            "hash": self.request.params['hash'],
            "filename": self.request.params['filename'],
        }
