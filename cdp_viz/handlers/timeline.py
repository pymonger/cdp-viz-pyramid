import logging, simplejson, pprint, re
from urllib2 import urlopen
from urllib import urlencode, quote
from datetime import datetime

from pyramid_handlers import action

from beaker.cache import CacheManager

import cdp_viz.handlers.base as base
import cdp_viz.models as model
from cdp_viz.lib.timeUtils import getDatetimeFromString, getISODateTimeString
from cdp_viz.lib.sparql import SESSION_SPARQL_TMPL, sparqlQuery
from cdp_viz.lib.sessionGraph import rdf2sessionGraph

log = logging.getLogger(__name__)

class Timeline(base.Handler):
    @action(renderer="timeline.mako")
    def index(self):
        return {
            "sessionId": self.request.params['sessionId'],
            "sessionId_nopound": self.request.params['sessionId'].replace('#', '%23'),
            "title": "Timeline for Session %s" % self.request.params['sessionId']
        }

    @action(renderer="json")
    def getSessionStartTime(self):
        """Return session start time."""

        sessionId = self.request.params['sessionId']
        d = sparqlQuery(SESSION_SPARQL_TMPL.substitute(uri=sessionId))
        g = eval(rdf2sessionGraph(d, {'processes': {}, 'processGraph': []}))
        return {'startTime': g['processes'][g['processGraph'][0][1]]['startTime']}

    @action(renderer="json")
    def getSessionTimelineData(self):
        """Return session timeline json."""
        
        entity_re = re.compile(r'http://provenance.jpl.nasa.gov/cdp#(.*)/.*$')
        sess_re = re.compile(r'(http://provenance.jpl.nasa.gov/cdp#Session/session/)(.*)$')
        
        sess_match = sess_re.search(self.request.params['sessionId'])
        if not sess_match: raise RuntimeError("Failed to match sess_re.")
        sessionId = "%s%s" % (sess_match.group(1), quote(sess_match.group(2)))
        d = sparqlQuery(SESSION_SPARQL_TMPL.substitute(uri=sessionId))
        g = eval(rdf2sessionGraph(d, {'processes': {}, 'processGraph': []}))
        
        retDict = {
            'dateTimeFormat': "iso8601",
            'wikiURL': "http://simile.mit.edu/shelf/",
            'wikiSection': "CDP Provenance",
            'events': []
        }
        
        agent_re = re.compile(r'#Person/agent/(.+?)/')
        proc_re = re.compile(r'#ProcessingStep/process/(.+?)/')
        
        #add process links in a flattened workflow
        trackNum = 0
        log.debug("agent: %s" % g['agent'][1])
        for cause, effect in g['processGraph']:
            trackNum += 1
            log.debug("cause: %s\neffect: %s" % (cause, effect))
            if cause == g['agent'][1]:
                match = agent_re.search(cause)
                if not match: raise RuntimeError("Failed to match agent_re.")
                agent = match.group(1)
                retDict['events'].append({
                    'start': g['processes'][effect]['startTime'],
                    'title': agent,
                    'durationEvent': False,
                    'icon' : "/wsgi/cdp/resources/images/timeline/dark-red-circle.png",        
                    'color' : 'red',
                    'trackNum': trackNum,
                    'description': cause
                })
                trackNum += 1
                
            match = proc_re.search(effect)
            if not match: raise RuntimeError("Failed to match proc_re.")
            title = match.group(1)
            start = getDatetimeFromString(g['processes'][effect]['startTime'])
            end = getDatetimeFromString(g['processes'][effect]['endTime'])
            if trackNum == 2:
                retDict['events'].append({
                    'start': g['processes'][effect]['startTime'],
                    'end': g['processes'][effect]['endTime'],
                    'title': title,
                    'durationEvent': True,
                    'tapeImage': "/wsgi/cdp/resources/images/timeline/blue_stripes.png",
                    'trackNum': trackNum,
                    'description': effect
                })
            else:
                td = end-start
                if td.days == 0 and td.seconds == 0:
                    retDict['events'].append({
                        'start': g['processes'][effect]['startTime'],
                        'end': g['processes'][effect]['endTime'],
                        'title': title,
                        'durationEvent': False,
                        'icon': "/wsgi/cdp/timeline/timeline_js/images/dull-blue-circle.png",
                        'trackNum': trackNum,
                        'description': effect
                    })
                else:
                    retDict['events'].append({
                        'start': g['processes'][effect]['startTime'],
                        'end': g['processes'][effect]['endTime'],
                        'title': title,
                        'durationEvent': True,
                        'trackNum': trackNum,
                        'description': effect
                    })
                
        return retDict
