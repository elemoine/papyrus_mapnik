papyrus_mapnik
==============

The overall goal of papyrus_mapnik is to ease creating `Mapnik
<http://mapnik.org>`_-based web services in `Pyramid
<http://docs.pylonsproject.org/docs/pyramid.html>`_ applications.

papyrus_mapnik can be used together with `papyrus
<http://pypi.python.org/pypi/papyrus>`_ to easily build MapFish-compliant web
services (see `MapFish Protocol
<http://trac.mapfish.org/trac/mapfish/wiki/MapFishProtocol>`_) outputing Mapnik
images.

Here is a request example::

    GET /countries.png?limit=100&offset=10&continent__eq=Africa&queryable=continent&img_width=1400&img_height=600&img_bbox=-180,-90,180,90

papyrus_mapnik extends the MapFish Protocol with specific parameters, namely
``img_width``, ``img_height``, and ``img_bbox``.

Dependencies
------------

papyrus_mapnik requires the Mapnik2 libs and Python bindings. papyrus_mapnik
doesn't require papyrus, so to use papyrus_mapnik together with papyrus both
packages must be expressed as dependencies of the Pyramid application.

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
a conventional way.

Let's also assume this application includes a read-only MapFish-compliant
(JSON) web service set up with a view function and a route to this view.

In ``MyApp/myapp/__init__.py`` the route is defined as follows::

    config.add_route('countries_vector', '/countries.json')

In ``MyApp/myapp/views.py`` the view function is defined as follows::

    @view_config(route_name='countries_vector', renderer='geojson')
    def countries(request)
        return proto.read(request)

Now we want to use papyrus_mapnik to extend this web service so it can also
output images. For that we define a new route::

    config.add_route('countries_raster', '/countries.png')

And add another view configuration to the view function::

    @view_config(route_name='countries_raster', renderer='myapp:population.xml')
    @view_config(route_name='countries_vector', renderer='geojson')
    def countries(request)
        return proto.read(request)

In the above example it is assumed that a Mapnik configuration file named
population.xml is located in the ``MyApp/myapp`` directory. The renderer
parameter is an `asset specification
<http://docs.pylonsproject.org/projects/pyramid/1.0/narr/assets.html#understanding-asset-specifications>`_.

Run the tests
-------------

To run the tests install the ``nose``, ``mock`` and ``coverage`` packages in
the Python environment, and execute::

    $ nosetests --with-coverage
