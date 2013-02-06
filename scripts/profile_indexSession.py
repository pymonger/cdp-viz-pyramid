import cProfile
from cdp_viz.handlers.services.solr import indexSession

def main():
    sessionURI = 'http://provenance.jpl.nasa.gov/cdp#OPMGraph/session/CloudSat_AIRS_Matchups-sciflo-appliance.localdomain-sflops-2012-02-04T19_40_57.800985097885Z-23094'
    indexSession(sessionURI)

if __name__ == "__main__":
    cProfile.run('main()', 'statsprof')
