papyrus_mapnik
==============

The overall goal of papyrus_mapnik is to ease creating `Mapnik
<http://mapnik.org>`_-based web services in `Pyramid
<http://docs.pylonsproject.org/docs/pyramid.html>`_ applications.  Towards this
goal papyrus_mapnik provides adapters, bridges, whatever between Pyramid and
Mapnik.

More specifically, papyrus_mapnik can be used together with `papyrus
<http://pypi.python.org/pypi/papyrus>`_ to easily build MapFish-compliant web
services (see `MapFish Protocol
<http://trac.mapfish.org/trac/mapfish/wiki/MapFishProtocol>`_) that output
Mapnik images.

Here is a request looks like::

    GET /countries.png?queryable=cont&cont__eq=Africa&img_width=1400&img_height=600&img_bbox=-180,-90,180,90

The ``queryable`` and ``${attr}__eq`` are parameters defined by the MapFish
Protocol. papyrus_mapnik extends the MapFish Protocol with specific parameters,
namely ``img_width``, ``img_height``, and ``img_bbox``.

Why?
----

"MapServer, GeoServer, Mapnik OGCServer, and others are doing a great job at
serving images with WMS, so why doing that?"

Beacause it provides simple and nice HTTP interfaces for requesting images with
filters. And because it provides extreme flexibility and customizability. Think
security!

Dependencies
------------

papyrus_mapnik requires the Mapnik2 libs and Python bindings. papyrus_mapnik
doesn't require papyrus, so to use papyrus_mapnik together with papyrus both
packages must be dependencies of the Pyramid application.

Install
-------

papyrus_mapnik can be installed with ``easy_install``::

    $ easy_install papyrus_mapnik

Often you'll want to set papyrus_mapnik as a dependency of your Pyramid app,
which is done by adding ``papyrus_mapnik`` to the ``install_requires`` list
defined in the Pyramid app's ``setup.py`` file.

Renderer
--------

papyrus_mapnik provides a *renderer* that can convert objects returned by
papyrus' MapFish implementation (``papyrus.protocol``) into Mapnik
images wrapped in Pyramid Response objects. Conceptually the renderer is an
adapter between objects of different types, and of different libraries.

Usage
-----

Let's assume we have ``MyApp`` Pyramid application, structured in
a conventional way. Let's also assume this application defines
a MapFish web service, set up with a view function like this::

    @view_config(route_name='countries_vector', renderer='geojson')
    def countries(request)
        return proto.read(request)

With papyrus_mapnik this web service can be extended to output images.  This is
done by

1. registering the renderer provided by papyrus_mapnik
   (``myapp/__init__.py``)::

    from papyrus_mapnik.renderers import MapnikRendererFactory
    config.add_renderer('.xml', MapnikRendererFactory)

2. adding a new configuration to the view function (``myapp/views.py``)::

    @view_config(route_name='countries_raster', renderer='myapp:population.xml')
    @view_config(route_name='countries_vector', renderer='geojson')
    def countries(request)
        return proto.read(request)

3. and adding a route to this view (``myapp/__init__.py``)::

    config.add_route('countries_vector', '/countries.json')

In the above example it is assumed that a Mapnik configuration file named
population.xml is located in the ``MyApp/myapp`` directory. The renderer
parameter is an `asset specification
<http://docs.pylonsproject.org/projects/pyramid/1.0/narr/assets.html#understanding-asset-specifications>`_.

Run the tests
-------------

To run the tests install the ``nose``, ``mock`` and ``coverage`` packages in
the Python environment, and execute::

    $ nosetests --with-coverage
