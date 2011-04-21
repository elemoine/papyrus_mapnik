from pyramid.config import Configurator

def main(global_config, **settings):
    """ Return the Pyramid application.
    """
    config = Configurator(settings=settings)
    config.include(includeme)
    return config.make_wsgi_app()
