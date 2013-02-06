'''
 sesssionGraph.py -- Simple tools to parse SPARQL-query return into simple
                     graph data structure.

'''

import sys, os, re, types, pprint
import simplejson

from timeUtils import getDatetimeFromString

class UnknownQueryResponse(RuntimeError): pass
class UnknownGraphEdgeType(RuntimeError): pass

def getExposedUri(aUri):
    return aUri.replace('file://iearth.jpl.nasa.gov/usr2/home/sflops',
                        'http://iearth.jpl.nasa.gov') \
               .replace('file://iearth.jpl.nasa.gov/home/sflops/sciflo/share',
                        'http://iearth.jpl.nasa.gov') \
               .replace('file://iearth.jpl.nasa.gov/data1',
                        'http://iearth.jpl.nasa.gov/sciflo')
    
def rdf2sessionGraph(rdf, session={'processes': {}, 'processGraph': []}):
    """Parse JSON return from SPARQL query for session graph.
Return simple session graph data structure in JSON that can be further modified
for various visualizations.
    """
    if isinstance(rdf, types.StringTypes): rdf = simplejson.loads(rdf)
    if 'edge' not in rdf['head']['vars']:
        raise UnknownQueryResponse('Expected Session Graph.')
    
    #parse into data structures to help determine process order
    firstProc = None
    stimes = {}
    informed = {}
    agent = None
    for b in rdf['results']['bindings']:
        # first process
        if 'edge' not in b and 'cause' not in b:
            effect = b['effect']['value']
            start = getDatetimeFromString(b['stime']['value'])
            stimes.setdefault(start, []).append(effect)
            firstProc = effect
        else:
            edge = b['edge']['value']
            cause = b['cause']['value']
            effect = b['effect']['value']
            if '#wasInformedBy' in edge:
                start = getDatetimeFromString(b['stime']['value'])
                stimes.setdefault(start, []).append(effect)
                informed[effect] = cause
            elif '#wasAssociatedWith' in edge:
                agent = cause
    
    #build process graph
    procGraph = []
    for start in sorted(stimes):
        effects = stimes[start]
        for effect in effects:
            if effect not in informed: procGraph.insert(0, (agent, effect))
            else: procGraph.append((informed[effect], effect))
    session['processGraph'] = procGraph
    
    s = session
    firstProcInfo = None
    for b in rdf['results']['bindings']:
        if 'edge' not in b:
            firstProcInfo = b
            processUri = b['effect']['value']
            process = alias(processUri, 'process')
            s['processes'].setdefault(processUri, {})['shortname'] = process
            s['processes'][processUri]['startTime'] = b['stime']['value']
            s['processes'][processUri]['endTime'] = b['etime']['value']
            entityType = 'software_file'
            entityUri = getExposedUri(b['exec']['value'])
            entity = alias(entityUri, 'entity')
            if (entity, entityUri) not in processes[processUri].setdefault(entityType, []):
                processes[processUri].setdefault(entityType, []).append( (entity, entityUri) )
            continue
        edge = b['edge']['value']
        if '#wasAssociatedWith' in edge:
            agentUri = b['cause']['value']
            processUri = b['effect']['value']
            agent = alias(agentUri, 'agent')
            process = alias(processUri, 'process')
            s['agent'] = (agent, agentUri)
            s['processes'].setdefault(processUri, {})['shortname'] = process
            continue
        elif '#wasInformedBy' in edge:
            process1Uri = b['cause']['value']
            process2Uri = b['effect']['value']
            process1 = alias(process1Uri, 'process')
            process2 = alias(process2Uri, 'process')
            s['processes'].setdefault(process1Uri, {})['shortname'] = process1
            s['processes'].setdefault(process2Uri, {})['shortname'] = process2
            s['processes'][process2Uri]['startTime'] = b['stime']['value']
            s['processes'][process2Uri]['endTime'] = b['etime']['value']
            entityType = 'software_file'
            entityUri = getExposedUri(b['exec']['value'])
            entity = alias(entityUri, 'entity')
            if (entity, entityUri) not in processes[process2Uri].setdefault(entityType, []):
                processes[process2Uri].setdefault(entityType, []).append( (entity, entityUri) )
            continue
        elif '#used' in edge:
            entityType = 'inputs'
            entityUri = getExposedUri(b['cause']['value'])
            processUri = b['effect']['value']
        elif '#generated' in edge:
            entityUri = getExposedUri(b['effect']['value'])
            processUri = b['cause']['value']
            entityType = 'outputs'
        else:
            raise UnknownGraphEdgeType('edge: %s' % edge)
        
        process = alias(processUri, 'process')
        processes = s['processes']
        processes.setdefault(processUri, {})['shortname'] = process
        entity = alias(entityUri, 'entity')
        processes[processUri].setdefault(entityType, []).append( (entity, entityUri) )
    session = simplejson.dumps(s)
    return session


def alias(uri, typeHint=None,
          converters={'agent': (r'^.*#Person/agent/([^/]+)/.*$', r'U_\1'),
                      'process': [(r'^.*#ProcessingStep/process/([^/]+)/(....-..-..)T.*$', r'P_\1'),
                                  (r'^.*#Session/session/(.*?)-.*$', r'MCP_\1')],
                      'entity': [(r'^.*/(.*?\.hdf)/.*$', r'\1'),
                                   (r'^.*/(.*?\.pkl)/.*$', r'\1'),
                                   (r'^.*/(.*?\.nc)/.*$', r'\1'),
                                   (r'^.*/(.*?\.txt)/.*$', r'\1'),
                                   (r'^.*/(.*?\.txt.gz)/.*$', r'\1'),
                                   (r'^.*/(.*?\.sf\.xml)/.*$', r'\1'),
                                   (r'^.*/(varlist.json)/.*$', r'\1'),
                                   (r'^.*/(.*?\.py)/.*$', r'\1'),
                                   (r'^.*/(.*?\.pyc)/.*$', r'\1'),
                                   (r'^.*/(.*?\.so.*?)/.*$', r'\1'),
                                   (r'^.*/(.*?\.txt)$', r'\1'),
                                   (r'^.*/(.*?\.txt.gz)/.*$', r'\1'),
                                   (r'^.*/(CER_SSF_Aqua.*?)/.*$', r'\1'),
                                   (r'^.*/(.*?)/\d{4}-\d{2}-\d{2}T\d{2}_\d{2}_\d{2}$', r'\1'),
                                  ]}):
    '''Use regular expressions to derive short names from provenance URI's.'''
    if typeHint is not None:
        if typeHint == 'agent':
            patt, repl = converters[typeHint]
            if re.search(patt, uri):
                return re.sub(patt, repl, uri)
    if typeHint is None or typeHint in ('entity', 'process'):
        if typeHint is None: typeHint = 'entity'
        for patt, repl in converters[typeHint]:
            if re.search(patt, uri):
                return re.sub(patt, repl, uri)
    print >>sys.stderr, 'No alias: %s' % uri
    return uri


def printGraph(session, outs=sys.stdout):
    '''Pretty print session graph information.'''
    s = session
    agent = s['agent']
    print >>outs, "{agent: ('%s', '%s')," % tuple(agent)
    print >>outs, " processGraph: "
    for ps in s['processGraph']:
        print >>outs, "   ('%s', '%s')," % tuple(ps)
    processes = s['processes']
    print >>outs, " processes: "
    for k in processes:
        p = processes[k]
        print >>outs, "   '%s':" % k
        print >>outs, "     uri: '%s':" % p['uri']
        print >>outs, "     inputs:"
        for a in p.get('inputs', []):
#            print >>outs, "       ('%s', '%s')," % tuple(a)
            print >>outs, "       '%s'," % a[0]
        print >>outs, "     outputs:"
        for a in p.get('outputs', []):
#            print >>outs, "       ('%s', '%s')," % tuple(a)
            print >>outs, "       '%s'," % a[0]
        

def main():
    f = sys.argv[1]
    sparql_response_json = open(f, 'r').read()
    sessionGraph = rdf2sessionGraph(sparql_response_json)
    s = simplejson.loads(sessionGraph)
    printGraph(s, sys.stderr)
    print sessionGraph
    
if __name__ == '__main__':
    main()
