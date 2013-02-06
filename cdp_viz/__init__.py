from pyramid.config import Configurator
import akhet
import pyramid_beaker
import sqlahelper
import sqlalchemy

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    # Here you can insert any code to modify the ``settings`` dict.
    # You can:
    # * Add additional keys to serve as constants or "global variables" in the
    #   application.
    # * Set default values for settings that may have been omitted.
    # * Override settings that you don't want the user to change.
    # * Raise an exception if a setting is missing or invalid.
    # * Convert values from strings to their intended type.

    # Create the Pyramid Configurator.
    config = Configurator(settings=settings)
    config.include("pyramid_handlers")
    config.include("akhet")

    # Initialize database
    engine = sqlalchemy.engine_from_config(settings, prefix="sqlalchemy.")
    sqlahelper.add_engine(engine)
    config.include("pyramid_tm")

    # Configure Beaker sessions and caching
    session_factory = pyramid_beaker.session_factory_from_settings(settings)
    config.set_session_factory(session_factory)
    pyramid_beaker.set_cache_regions_from_settings(settings)

    # Configure renderers and event subscribers
    config.add_renderer(".html", "pyramid.mako_templating.renderer_factory")
    config.add_subscriber("cdp_viz.subscribers.create_url_generator",
        "pyramid.events.ContextFound")
    config.add_subscriber("cdp_viz.subscribers.add_renderer_globals",
                          "pyramid.events.BeforeRender")

    # Set up view handlers
    config.include("cdp_viz.handlers")

    # Set up other routes and views
    # ** If you have non-handler views, create create a ``cdp_viz.views``
    # ** module for them and uncomment the next line.
    #
    #config.scan("cdp_viz.views")

    # Mount a static view overlay onto "/". This will serve, e.g.:
    # ** "/robots.txt" from "cdp_viz/static/robots.txt" and
    # ** "/images/logo.png" from "cdp_viz/static/images/logo.png".
    #
    config.add_static_route("cdp_viz", "static", cache_max_age=3600)

    # Mount a static subdirectory onto a URL path segment.
    # ** This not necessary when using add_static_route above, but it's the
    # ** standard Pyramid way to serve static files under a URL prefix (but
    # ** not top-level URLs such as "/robots.txt"). It can also serve files from
    # ** third-party packages, or point to an external HTTP server (a static
    # ** media server).
    # ** The first commented example serves URLs under "/static" from the
    # ** "cdp_viz/static" directory. The second serves URLs under 
    # ** "/deform" from the third-party ``deform`` distribution.
    #
    #config.add_static_view("static", "cdp_viz:static")
    #config.add_static_view("deform", "deform:static")

    return config.make_wsgi_app()
