import logging

from pyramid_handlers import action

import cdp_viz.handlers.base as base
import cdp_viz.models as model

log = logging.getLogger(__name__)

class Main(base.Handler):
    @action(renderer="faceted_search.mako")
    def index(self):
        return {
            "project":"cdp_viz",
            "title": "Faceted Browsing"
        }
        
