import decimal
import datetime

from pyramid.asset import abspath_from_asset_spec

from mapnik import (MemoryDatasource, Feature, Box2d, Map, Image,
                    load_map, render)

from shapely.geometry import asShape


class MapnikRenderer(object):
    """
    """

    def _create_datasource(self, collection):
        """ Create a Mapnik memory datasource from a feature collection.
        """
        ds = MemoryDatasource()
        for feature in collection.features:
            properties = dict(feature.properties)
            for k, v in properties.iteritems():
                if isinstance(v, decimal.Decimal):
                    properties[k] = float(v)
                elif isinstance(v, (datetime.date, datetime.datetime)):
                    properties[k] = str(v)
            f = Feature(feature.id, **properties)
            f.add_geometries_from_wkb(asShape(feature.geometry).wkb)
            ds.add_feature(f)
        return ds

    def _set_layer_in_map(self, _map, layer_name):
        layer = None
        for i, l in enumerate(_map.layers):
            if l.name != layer_name:
                del _map.layers[i]
            else:
                layer = l
        return layer

    def __call__(self, info):
        mapfile = abspath_from_asset_spec(info.name)

        def _render(value, system):
            request = system['request']

            if not isinstance(value, tuple):
                value = (None, value)

            layer_name, collection = value

            if not hasattr(collection, 'features'):
                raise ValueError('renderer is not passed a feature collection')

            # get image width and height
            try:
                img_width = int(request.params.get('img_width', 256))
            except:
                request.response_status = 400
                return 'incorrect img_width'
            try:
                img_height = int(request.params.get('img_height', 256))
            except:
                request.response_status = 400
                return 'incorrect img_height'

            # get image format
            try:
                img_format = request.params.get(
                                 'img_format',
                                 request.matchdict.get('format', 'png'))
                img_format = str(img_format)
            except:
                request.response_status = 400
                return 'incorrect img_format'

            # get image bbox
            img_bbox = request.params.get('img_bbox',
                                          request.params.get('bbox'))
            if img_bbox:
                try:
                    img_bbox = map(float, img_bbox.split(','))
                except ValueError:
                    request.response_status = 400
                    return 'incorrect img_bbox'
                img_bbox = Box2d(*img_bbox)

            m = Map(img_width, img_height)
            load_map(m, mapfile)

            if len(m.layers) == 0:
                raise ValueError('no layer in the mapnik map')

            # if no layer_name is provided then, by convention, use
            # the first layer in the mapnik map
            if layer_name is None:
                layer_name = m.layers[0].name

            layer = self._set_layer_in_map(m, layer_name)
            layer.datasource = self._create_datasource(collection)

            m.zoom_to_box(img_bbox or layer.envelope())

            im = Image(img_width, img_height)
            render(m, im, 1, 1)

            # get the image format from the request

            request.response.content_type = 'image/%s' % img_format
            return im.tostring(img_format)

        return _render
