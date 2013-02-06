import logging, simplejson, pprint, re, os, sys
from pydot import Dot, Subgraph, Node, Edge
from tempfile import mkstemp

from utils import getXmlEtree, xpath, pprintXml

log = logging.getLogger(__name__)

def getSessionSVG(vizData):
    """Take session visualization data and return svg."""
    
    graph = Dot('graphname', graph_type='digraph')
    
    #loop create all nodes and store by uri
    nodeDict = {}
    for i, nodeData in enumerate(vizData['nodes']):
        uri = nodeData['uri']
        nodeDict[uri] = str(i)
        graph.add_node(Node(str(i)))
        
    #add edges by links
    for linkData in vizData['links']:
        snode = nodeDict[vizData['nodes'][linkData['source']]['uri']]
        tnode = nodeDict[vizData['nodes'][linkData['target']]['uri']]
        graph.add_edge(Edge(snode, tnode))
    
    #get svg of graph
    tmp, file = mkstemp()
    graph.write_svg(file)
    svg = open(file).read()
    os.unlink(file)
    
    #f = open('/tmp/session/session.svg', 'w')
    #f.write("%s\n" % svg)
    #f.close()

    return svg

def addGraphvizPositions(vizData):
    """Take viz data and add positions as determined by graphviz."""
    
    #get svg
    svg = getSessionSVG(vizData)
    
    #parse svg
    #get xml etree
    et, nsdict = getXmlEtree(svg)
    #log.debug(nsdict)
    
    #loop over each node and set x and y positions
    min_y = 0
    for i, nodeData in enumerate(vizData['nodes']):
        uri = nodeData['uri']
        elElt = et.xpath('.//_:g/_:ellipse[../_:title = "%s"]' % str(i), namespaces=nsdict)
        if len(elElt) != 1: raise RuntimeError("Failed to xpath query node %s." % str(i))
        else: elElt = elElt[0]
        nodeData['gv_x'] = int(eval(elElt.get('cx')))
        nodeData['gv_y'] = int(eval(elElt.get('cy')))
        if nodeData['gv_y'] < min_y: min_y = nodeData['gv_y']
        
    #move y values into the positive
    for nodeData in vizData['nodes']: nodeData['gv_y'] -= min_y
        
    return vizData
