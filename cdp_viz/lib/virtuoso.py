import os, subprocess, shutil
from tempfile import mkdtemp

ISQL_PATH = "/usr/local/virtuoso/bin/isql"

def isql(cmd):
    if not cmd.endswith(";"): raise RuntimeError("ISQL command must end with semicolon.")
    proc = subprocess.Popen(ISQL_PATH, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    return proc.communicate(cmd)

def bulk_import_rdf(graphURI, triples):
    d = mkdtemp()
    f = open(os.path.join(d, 'triples.ttl'), 'w')
    f.write("%s" % triples)
    f.close()
    f = open(os.path.join(d, 'triples.ttl.graph'), 'w')
    f.write("%s" % graphURI)
    f.close()
    isql("ld_dir('%s', '%s', '%s');" % (d, '*.ttl', graphURI))
    isql("rdf_loader_run();")
    shutil.rmtree(d)

if __name__ == "__main__":
    graphURI = "http://provenance.jpl.nasa.gov/cdp#OPMGraph/session/CloudSat_AIRS_Matchups-sciflo-appliance.localdomain-sflops-2012-02-04T19_40_57.800985097885Z-23094"
    triples = open('/home/cdpops/tmp/virtuoso_bulk_upload/test/triples.ttl').read()
    bulk_import_rdf(graphURI, triples)
