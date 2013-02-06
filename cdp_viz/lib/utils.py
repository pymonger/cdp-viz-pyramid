import re, urllib, os
from urllib2 import urlopen
from StringIO import StringIO
from lxml.etree import XMLParser, parse, tostring

NS = {
    'atom': 'http://www.w3.org/2005/Atom',
    'os': 'http://a9.com/-/spec/opensearch/1.1/',
    'georss': 'http://www.georss.org/georss/10',
    'geo': 'http://a9.com/-/opensearch/extensions/geo/1.0/',
    'time': 'http://a9.com/-/opensearch/extensions/time/1.0/'
}

def validateDirectory(dir, mode=0755, noExceptionRaise=False):
    """Validate that a directory can be written to by the current process and return 1.
    Otherwise, try to create it.  If successful, return 1.  Otherwise return None.
    """

    if os.path.isdir(dir):
        if os.access(dir, 7): return 1
        else: return None
    else:
        try:
            os.makedirs(dir, mode)
            os.chmod(dir, mode)
        except:
            if noExceptionRaise: pass
            else: raise
        return 1

def formatIsoDate(dt, tm):
    """Return ISO 8601 formatted date time."""
    
    iso = ''
    if dt != '':
        match = re.search(r'^(\d{2})/(\d{2})/(\d{4})$', dt)
        if not match:
            raise RuntimeError("Failed to extract date from %s." % dt)
        iso += "%s-%s-%sT" % (match.group(3), match.group(1), match.group(2))
        if tm != '':
            match = re.search(r'^(\d{2}):(\d{2})', tm)
            if not match:
                raise RuntimeError("Failed to extract time from %s." % tm)
            iso += "%s:%s:00Z" % match.groups()
        else: iso += "00:00:00Z"
    return iso

def formatBbox(minLon, minLat, maxLon, maxLat):
    """Return OpenSearch formatted bbox."""
    
    for val in [minLon, minLat, maxLon, maxLat]:
        if val in [None, '']: return ''
    return ','.join([minLon, minLat, maxLon, maxLat])

def formatUrl(url, searchTerms, startTime, endTime, bbox, limit=None, start=None):
    """Return interpolated and encoded OpenSearch url."""
    
    #interpolate searchTerms if not empty; otherwise remove parameter
    if searchTerms == '':
        url = re.sub(r'(&?\w+?)={(?:os:)?searchTerms\??}', '', url)
    else:
        url = re.sub(r'(&?\w+?)={(?:os:)?searchTerms\??}', r'\1=%s' %
                     urllib.quote_plus(searchTerms), url)
        
    #interpolate startTime if not empty; otherwise remove parameter
    if startTime == '':
        url = re.sub(r'(&?\w+?)={time:start\??}', '', url)
    else:
        url = re.sub(r'(&?\w+?)={time:start\??}', r'\1=%s' %
                     urllib.quote_plus(startTime), url)
        
    #interpolate endTime if not empty; otherwise remove parameter
    if endTime == '':
        url = re.sub(r'(&?\w+?)={time:end\??}', '', url)
    else:
        url = re.sub(r'(&?\w+?)={time:end\??}', r'\1=%s' %
                     urllib.quote_plus(endTime), url)
        
    #interpolate bbox if not empty; otherwise remove parameter
    if bbox == '':
        url = re.sub(r'(&?\w+?)={geo:box\??}', '', url)
        url = re.sub(r'(&?\w+?)={georss:box\??}', '', url)
    else:
        url = re.sub(r'(&?\w+?)={geo:box\??}', r'\1=%s' %
                     urllib.quote_plus(bbox), url)
        url = re.sub(r'(&?\w+?)={georss:box\??}', r'\1=%s' %
                     urllib.quote_plus(bbox), url)
        
    #interpolate count if not empty; otherwise remove parameter
    if limit is None:
        url = re.sub(r'(&?\w+?)={(?:os:)?count\??}', '', url)
    else:
        url = re.sub(r'(&?\w+?)={(?:os:)?count\??}', r'\1=%s' %
                     urllib.quote_plus(str(limit)), url)
        
    #interpolate startIndex if not empty; otherwise remove parameter
    if start is None:
        url = re.sub(r'(&?\w+?)={(?:os:)?startIndex\??}', '', url)
    else:
        url = re.sub(r'(&?\w+?)={(?:os:)?startIndex\??}', r'\1=%s' %
                     urllib.quote_plus(str(start)), url)
        
    #interpolate startPage if not empty; otherwise remove parameter
    if limit is None:
        url = re.sub(r'(&?\w+?)={(?:os:)?startPage\??}', '', url)
    else:
        if start is not None: startPage = start/limit+1
        else: startPage = 1
        url = re.sub(r'(&?\w+?)={(?:os:)?startPage\??}',
                     urllib.quote_plus(str(startPage)), url) 
        
    #clear out other template items
    url = re.sub(r'(&?\w+?)={\w+?:\w+\??}', '', url)
    
    #replace ' ' with '+'
    url = url.replace(' ', '+')
    
    return url

def getXmlEtree(xml):
    """Return a tuple of [lxml etree element, prefix->namespace dict].
    """

    parser = XMLParser(remove_blank_text=True)
    if xml.startswith('<?xml') or xml.startswith('<'):
        return (parse(StringIO(xml), parser).getroot(),
                getNamespacePrefixDict(xml))
    else:
        if os.path.isfile(xml): xmlStr = open(xml).read()
        else: xmlStr = urlopen(xml).read()
        return (parse(StringIO(xmlStr), parser).getroot(),
                getNamespacePrefixDict(xmlStr))

def getNamespacePrefixDict(xmlString):
    """Take an xml string and return a dict of namespace prefixes to
    namespaces mapping."""
    
    nss = {} 
    defCnt = 0
    matches = re.findall(r'\s+xmlns:?(\w*?)\s*=\s*[\'"](.*?)[\'"]', xmlString)
    for match in matches:
        prefix = match[0]; ns = match[1]
        if prefix == '':
            defCnt += 1
            prefix = '_' * defCnt
        nss[prefix] = ns
    return nss

def xpath(elt, xp, ns, default=None):
    """
    Run an xpath on an element and return the first result.  If no results
    were returned then return the default value.
    """
    
    res = elt.xpath(xp, namespaces=ns)
    if len(res) == 0: return default
    else: return res[0]
    
def pprintXml(et):
    """Return pretty printed string of xml element."""
    
    return tostring(et, pretty_print=True)

def getExcerpt(elt, ns):
    """Return build short description from atom entry."""
    
    excpt = []
    
    #get georss:box or geo:box
    box = xpath(elt, './georss:box/text()', ns)
    if box is None:
        box = xpath(elt, './geo:box/text()', ns)
        if box is not None:
            excpt.append("<b>geo:box:</b> " + box)
    else: excpt.append("<b>georss:box:</b> " + box)
    
    #get time:start and end
    start = xpath(elt, './time:start/text()', ns)
    if start is not None: excpt.append("<b>time:start:</b> " + start)
    end = xpath(elt, './time:end/text()', ns)
    if end is not None: excpt.append("<b>time:end:</b> " + end)
    
    return ", &nbsp;".join(excpt)

class Feed(object):
    """Callable class for reading data from a url."""
    def __init__(self, url): self.url = url
    def __call__(self): return urlopen(self.url).read()
    