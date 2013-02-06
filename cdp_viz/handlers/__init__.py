"""View handlers package.
"""

def includeme(config):
    """Add the application's view handlers.
    """
    config.add_handler("home", "/", "cdp_viz.handlers.main:Main",
                       action="index")
    config.add_handler("solr", "/solr", "cdp_viz.handlers.solr:Solr",
                       action="index")
    config.add_handler("solr_action", "/solr/{action}",
                       "cdp_viz.handlers.solr:Solr")
    config.add_handler("timeline", "/timeline", "cdp_viz.handlers.timeline:Timeline",
                       action="index")
    config.add_handler("timeline_action", "/timeline/{action}",
                       "cdp_viz.handlers.timeline:Timeline")
    config.add_handler("fdl", "/fdl", "cdp_viz.handlers.fdl:ForceDirectedLayout",
                       action="index")
    config.add_handler("fdl_action", "/fdl/{action}",
                       "cdp_viz.handlers.fdl:ForceDirectedLayout")
    config.add_handler("reproduce", "/reproduce", "cdp_viz.handlers.reproduce:Reproduce",
                       action="index")
    config.add_handler("reproduce_action", "/reproduce/{action}",
                       "cdp_viz.handlers.reproduce:Reproduce")
    config.add_handler("solr_services", "/services/solr", "cdp_viz.handlers.services.solr:Solr",
                       action="index")
    config.add_handler("solr_services_action", "/services/solr/{action}",
                       "cdp_viz.handlers.services.solr:Solr")
    config.add_handler("logfile_services", "/services/logfile", "cdp_viz.handlers.services.logfile:Logfile",
                       action="index")
    config.add_handler("logfile_services_action", "/services/logfile/{action}",
                       "cdp_viz.handlers.services.logfile:Logfile")
    config.add_handler("rdf_services", "/services/rdf", "cdp_viz.handlers.services.rdf:Rdf",
                       action="index")
    config.add_handler("rdf_services_action", "/services/rdf/{action}",
                       "cdp_viz.handlers.services.rdf:Rdf")
    config.add_handler("print_services", "/services/print", "cdp_viz.handlers.services.print:Print",
                       action="index")
    config.add_handler("print_services_action", "/services/print/{action}",
                       "cdp_viz.handlers.services.print:Print")
    config.add_handler("dl_services", "/services/dl", "cdp_viz.handlers.services.dl:Download",
                       action="index")
    config.add_handler("dl_services_action", "/services/dl/{action}",
                       "cdp_viz.handlers.services.dl:Download")
    config.add_handler("main", "/{action}", "cdp_viz.handlers.main:Main",
        path_info=r"/(?!favicon\.ico|robots\.txt|w3c|__history__\.html)")
