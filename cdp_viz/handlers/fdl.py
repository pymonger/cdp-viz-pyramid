import logging, simplejson, pprint, re, os, sys
from urllib2 import urlopen
from urllib import urlencode, quote
from datetime import datetime
from string import Template
from Levenshtein import ratio, median
from tempfile import mkstemp

from pyramid_handlers import action

from beaker.cache import CacheManager

import cdp_viz.handlers.base as base
import cdp_viz.models as model
from cdp_viz.lib.timeUtils import getDatetimeFromString, getISODateTimeString
from cdp_viz.lib.sparql import (SESSION_SPARQL_TMPL, sparqlQuery,
SESSION_BY_ENTITY_MD5_SPARQL_TMPL, MD5_SPARQL_TMPL, LANDING_PAGE_SPARQL_TMPL)
from cdp_viz.lib.sessionGraph import rdf2sessionGraph
from cdp_viz.lib.graphviz import addGraphvizPositions

log = logging.getLogger(__name__)

def bundleEntities(ents):
    """
    Bundle entities if they exceed a reasonable limit using Levenshtein
    distance ratio to bundle similar entities together.
    http://stackoverflow.com/questions/682367/good-python-modules-for-fuzzy-string-comparison
    """
    
    if len(ents) < 50: return ents
    bundleDict = {}
    matchedAlready = set()
    retEnts = []
    ents2 = ents
    for a, aUri in sorted(ents):
        if a in matchedAlready: continue
        for a2, a2Uri in sorted(ents2):
            if a == a2 or a2 in matchedAlready: continue
            rat = ratio(aUri, a2Uri)
            if rat > .8:
                bundleDict.setdefault(a, [[a, aUri]]).append([a2, a2Uri])
                matchedAlready.add(a)
                matchedAlready.add(a2)
    #pprint.pprint(bundleDict)
    for a, aUri in ents:
        if a not in matchedAlready: retEnts.append([a, aUri])
    for bundle in bundleDict:
        #get approximate generalized median string as collection name
        medStr = median([i[0] for i in bundleDict[bundle]])
        retEnts.append(["collection:%s" % medStr,
                        ', '.join([i[1] for i in bundleDict[bundle]])])
    return retEnts

SO_RE = re.compile(r'.+\.so(?:\..+)?$')
LIB_RE = re.compile(r'/usr/lib/')
URND_RE = re.compile(r'/dev/urandom/')
LCLTM_RE = re.compile(r'/etc/localtime/')
MEM_RE = re.compile(r'/proc/meminfo/')
PY_RE = re.compile(r'/lib/python\d\.\d/')

def bundleSystemFiles(ents):
    """
    Bundle entities if they exceed a reasonable limit and are system files.
    """
    
    bundleDict = {}
    matchedAlready = set()
    retEnts = []
    for a, aUri in sorted(ents):
        if a in matchedAlready: continue
        if SO_RE.search(a) or LIB_RE.search(aUri) or URND_RE.search(aUri) or \
            LCLTM_RE.search(aUri) or MEM_RE.search(aUri):
            bundleDict.setdefault('system-files', []).append([a, aUri])
        elif PY_RE.search(aUri):
            bundleDict.setdefault('system-files-python', []).append([a, aUri])
        else: retEnts.append([a, aUri])
        matchedAlready.add(a)
    for bundle in bundleDict:
        retEnts.append(["collection:%s" % bundle,
                        ', '.join([i[1] for i in bundleDict[bundle]])])
    return retEnts

class ForceDirectedLayout(base.Handler):
    @action(renderer="fdl.mako")
    def index(self):
        return {
            "title": "Force Directed Layout",
            "sessionId": self.request.params['sessionId'],
            "experimental": self.request.params.get('experimental', 'false')
        }
        
    @action(renderer="json")
    def getSessionVizData(self):
        """Return sessions visualization data in json format."""
        
        ldos_tmpl = '%s/data/download?&filename=%s&hash=%s'
        
        #log.debug("getSessionVizData params: %s" % request.params)
        sessionId = self.request.params['sessionId']
        #log.debug("getSessionVizData sessionId: %s" %  sessionId)
        d = sparqlQuery(SESSION_SPARQL_TMPL.substitute(uri=sessionId))
        #f = open('/tmp/session/sparql.txt', 'w')
        #f.write("sessionId: %s\n" % sessionId)
        #simplejson.dump(simplejson.loads(d), f, indent=2)
        #f.close()
        
        g = simplejson.loads(rdf2sessionGraph(d, {'processes': {}, 'processGraph': []}))
        #f = open('/tmp/session/session.txt', 'w')
        #simplejson.dump(g, f, indent=2)
        #f.close()
        
        #get md5
        m = simplejson.loads(sparqlQuery(MD5_SPARQL_TMPL.substitute(uri=sessionId)))
        md5dict = {}
        for binding in m['results']['bindings']:
            md5dict[binding['entity']['value']] = binding['md5']['value']
        
        #generate viz dict
        nodes = []
        links = []
        inputEnts = {}
        outputEnts = {}
        vizDict = {'nodes': [], 'links': []}
        
        #add agent node
        vizDict['nodes'].append({'nodeName': g['agent'][0],
                                 'uri': g['agent'][1],
                                 'group': 1,
                                 'size': 1000,
                                 'shape': 'triangle-down'})
        nodes.append(g['agent'][1])
        
        #add process nodes and entities
        for pUri in g['processes']:
            p = g['processes'][pUri]['shortname']
            if 'software_file' in g['processes'][pUri]:
                swLink = g['processes'][pUri]['software_file'][0][0]
            else: swLink = ''
            vizDict['nodes'].append({'nodeName': p,
                                     'uri': pUri,
                                     'dlLink': swLink,
                                     'group': 2,
                                     'size': 3000,
                                     'shape': 'square'})
            nodes.append(pUri)
            
            #input entities
            if 'inputs' in g['processes'][pUri]:
                ents = bundleSystemFiles(g['processes'][pUri]['inputs'])
                ents = bundleEntities(ents)
                for a, aUri in ents:
                    if aUri in md5dict:
                        dlLink = ldos_tmpl % (self.request.registry.settings['ldos.url'], a, md5dict[aUri])
                    else: dlLink = None
                    if aUri not in nodes:
                        if a.startswith('collection:'):
                            vizDict['nodes'].append({'nodeName': a,
                                                    'uri': aUri,
                                                    'dlLink': dlLink,
                                                    'size': 1500,
                                                    'group': 3})
                        else:
                            vizDict['nodes'].append({'nodeName': a,
                                                    'dlLink': dlLink,
                                                    'uri': aUri,
                                                    'size': 1000,
                                                    'group': 3})
                        nodes.append(aUri)
                    inputEnts.setdefault(aUri)
                    
                    #add links
                    vizDict['links'].append({'source': nodes.index(aUri),
                                             'target': nodes.index(pUri),
                                             'type': 'input',
                                             'value': 1})
                        
            #output entities
            if 'outputs' in g['processes'][pUri]:
                ents = bundleEntities(g['processes'][pUri]['outputs'])
                for a, aUri in ents:
                    if aUri in md5dict:
                        dlLink = ldos_tmpl % (self.request.registry.settings['ldos.url'], a, md5dict[aUri])
                    else: dlLink = None
                    if aUri not in nodes:
                        if a.startswith('collection:'):
                            vizDict['nodes'].append({'nodeName': a,
                                                    'uri': aUri,
                                                    'dlLink': dlLink,
                                                    'size': 1500,
                                                    'group': 4})
                        else:
                            vizDict['nodes'].append({'nodeName': a,
                                                    'uri': aUri,
                                                    'dlLink': dlLink,
                                                    'size': 1000,
                                                    'group': 4})
                        nodes.append(aUri)
                    outputEnts.setdefault(aUri)
                        
                    #add links
                    vizDict['links'].append({'source': nodes.index(pUri),
                                             'target': nodes.index(aUri),
                                             'type': 'output',
                                             'value': 1})
                    
        #modify color of entities that are inputs and outputs or just outputs
        for aUri in nodes:
            if aUri in inputEnts and aUri in outputEnts:
                #print "%s is in both" % a
                for vdn in vizDict['nodes']:
                    if vdn['uri'] == aUri:
                        vdn['group'] = 5
                        #print vdn
                        break
            
        #add process links in a flattened workflow
        previousProc = None
        mainProc = None
        for cause, effect in g['processGraph']:
            if cause == g['agent'][1]:
                linkVal = 20
                mainProc = effect
            else: linkVal = 20
            
            #link processes
            if previousProc is None or cause != mainProc:
                if previousProc is None: linkType = 'controlled'
                else: linkType = 'triggered'
                vizDict['links'].append({'source': nodes.index(cause),
                                         'target': nodes.index(effect),
                                         'type': linkType,
                                         'value': linkVal})
            
            else:
                vizDict['links'].append({'source': nodes.index(previousProc),
                                         'target': nodes.index(effect),
                                         'type': 'triggered',
                                         'value': linkVal})
            previousProc = effect
        
        #f = open('/tmp/session/session.json', 'w')
        #simplejson.dump(vizDict, f, indent=2)
        #f.close()
        
        #add graphviz positions
        vizDict = addGraphvizPositions(vizDict)
        #f = open('/tmp/session/session2.json', 'w')
        #simplejson.dump(addGraphvizPositions(vizDict), f, indent=2)
        #f.close()
        
        return vizDict
    
    @action(renderer="string")
    def getNodeInfo(self):
        uri = self.request.params.get('uri')
        dlLink = self.request.params.get('dlLink')
        nodeName = self.request.params.get('nodeName')
        sessionURI = self.request.params.get('sessionURI')
        #log.debug("uri: %s" % uri)
        #log.debug("dlLink: %s" % dlLink)
        info = 'No info available.'
        if nodeName.startswith("collection:"):
            uri = '\n'.join([i.strip() for i in uri.split(',')])
            dlLink = '\n'.join([i.strip() for i in dlLink.split(',')])
            retHtml = Template("""<div style="padding:20px;">
                    <style type="text/css">
                    textarea
                    {
                        width:100%;
                    }
                    .textwrapper
                    {
                        border:1px solid #999999;
                        margin:5px 0;
                        padding:3px;
                    }
                    </style>
                    <b>URIs:</b><br/>
                    <div style="display: block;" id="rulesformitem" class="formitem">
                        <div class="textwrapper">
                            <textarea cols="2" rows="33" id="rules" readonly="true">$uris</textarea>
                        </div>
                    </div>
                    <!--
                    <b>Downloads:</b><br/>
                    <div style="display: block;" id="rulesformitem" class="formitem">
                        <div class="textwrapper">
                            <textarea cols="2" rows="15" id="rules" readonly="true">$dls</textarea>
                        </div>
                    </div>
                    -->
                    </div>""")
            return retHtml.substitute(uris=uri, dls=dlLink)
        
        landingPage = ""
        relatedSessionURIs = []
        if dlLink != '':
            hash = re.search(r'hash=(\w{32})', dlLink)
            if hash:
                ldos_tmpl = '%s/data/search?query=%s' % \
                    (self.request.registry.settings['ldos.url'], hash.group(1))
                ldos_res = simplejson.loads(urlopen(ldos_tmpl).read())['docs']
                if len(ldos_res) == 0: metadata = None
                else: metadata = ldos_res[0]['metadata'][0]
                if metadata is not None and metadata != '':
                    try:
                        info = simplejson.dumps(simplejson.loads(metadata), indent=2)
                    except: info = metadata
                
                #get sessions that have this entity
                d = simplejson.loads(sparqlQuery(
                    SESSION_BY_ENTITY_MD5_SPARQL_TMPL.substitute(md5=hash.group(1))))
                for result in d['results']['bindings']:
                    if result['entity']['value'] != uri and result['session']['value'] != sessionURI:
                        relatedSessionURIs.append((result['session']['value'], result['entity']['value']))

                #create link to landing page
                q = urlencode({
                    'q': '*:*',
                    'wt': 'json',
                    'fq': hash.group(1)
                })
                d = simplejson.loads(urlopen('http://localhost:8983/solr/select', q).read())
                if d['response']['numFound'] == 1 and 'landing_page' in d['response']['docs'][0]:
                    landingPage = d['response']['docs'][0]['landing_page']
                    landingPage = '<b>Dataset Web Page:</b> <a href="%s" target="_blank">%s</a><br/><br/>' % (landingPage, landingPage)

        #create link to visualize related sessions
        relatedSessionsHtml = []
        for relatedSessionURI, relatedEntityURI in relatedSessionURIs:
            relatedSessionsHtml.append('<a href="javascript:addSessionViz(\'%s\', \'%s\');">%s</a> ' % \
                (quote(relatedSessionURI), quote(relatedEntityURI), relatedSessionURI))
        if len(relatedSessionsHtml) > 0:
            relatedSessions = "<b>Related sessions:</b> "
            relatedSessions += ", ".join(relatedSessionsHtml)
            relatedSessions += "<br/><br/>"
        else: relatedSessions = ""

        #create link to reproduce sciflo
        reproduce = ""
        if re.search(r'.*\.sf\.xml$', nodeName):
            reproduce = "<b>Reproduce on AWS:</b> "
            reproduce += '<a href="reproduce?dlLink=%s" target="_blank">%s&nbsp;<img width="30" height="25" src="images/easy_button.jpg" onclick="var snd = new Audio(\'wav/cash-register.wav\');snd.play();"/></a>' % (dlLink, nodeName)
            reproduce += "<br/><br/>"
        elif re.search(r'^session_manifest\.txt$', nodeName):
            reproduce = "<b>Reproduce using CDE:</b> "
            reproduce += '<a href="services/dl/cde?sessionId=%s" target="_blank">%s&nbsp;<img width="30" height="25" src="images/easy_button.jpg" onclick="var snd = new Audio(\'wav/cash-register.wav\'); snd.play();"/></a>' % (quote(sessionURI), 'wget script')
            reproduce += "<br/><br/>"

        retHtml = Template("""<div style="padding:20px;">
            <b>URI:</b> $uri<br/><br/>
            $landingPage
            <b>Download:</b> <a href="$dlLink">$dlLink</a><br/><br/>
            $relatedSessions
            $reproduce
            <b>Info:</b><br/>
            <style type="text/css">
            textarea
            {
                width:100%;
            }
            .textwrapper
            {
                border:1px solid #999999;
                margin:5px 0;
                padding:3px;
            }
            </style>
            <div style="display: block;" id="rulesformitem" class="formitem">
                <div class="textwrapper">
                    <textarea cols="2" rows="28" id="rules" readonly="true">$info</textarea>
                </div>
            </div>
            </div>""")
        return retHtml.substitute(uri=uri, dlLink=dlLink, info=info, 
                                  relatedSessions=relatedSessions,
                                  reproduce=reproduce, landingPage=landingPage) #.replace('\n', '<br/>'))
