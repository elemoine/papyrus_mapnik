import decimal
import datetime

from pyramid.asset import abspath_from_asset_spec

from mapnik import (MemoryDatasource, Geometry2d, Feature, Box2d, Map, Image,
                    load_map, render)

from shapely.geometry import asShape


class MapnikRendererFactory:

    def __init__(self, info):
        self.mapfile = abspath_from_asset_spec(info.name)

    def _create_datasource(self, collection):
        """ Create a Mapnik memory datasource from a feature collection.
        """
        ds = MemoryDatasource()
        for feature in collection.features:
            wkt = asShape(feature.geometry).wkt
            geometry = Geometry2d.from_wkt(wkt)
            properties = dict(feature.properties)
            for k, v in properties.iteritems():
                if isinstance(v, decimal.Decimal):
                    properties[k] = float(v)
                elif isinstance(v, (datetime.date, datetime.datetime)):
                    properties[k] = str(v)
            ds.add_feature(Feature(feature.id, geometry, **properties))
        return ds

    def _set_layer_in_map(self, _map, layer_name):
        layer = None
        for i, l in enumerate(_map.layers):
            if l.name != layer_name:
                del _map.layers[i]
            else:
                layer = l
        return layer

    def __call__(self, value, system):
        request = system['request']

        if not isinstance(value, tuple):
            value = (None, value)

        layer_name, collection = value

        if not hasattr(collection, 'features'):
            raise ValueError('renderer is not passed a feature collection')

        # get image width and height
        try:
            width = int(request.params.get('img_width', 600))
        except:
            request.response_status = 400
            return 'incorrect width'
        try:
            height = int(request.params.get('img_height', 400))
        except:
            request.response_status = 400
            return 'incorrect height'

        # get image bbox
        bbox = request.params.get('img_bbox')
        if bbox:
            try:
                bbox = map(float, bbox.split(','))
            except ValueError:
                request.response_status = 400
                return 'incorrect img_bbox'
            bbox = Box2d(*bbox)

        m = Map(width, height)
        load_map(m, self.mapfile)

        if len(m.layers) == 0:
            raise ValueError('no layer in the mapnik map')

        # if no layer_name is provided then, by convention, use
        # the first layer in the mapnik map
        if layer_name is None:
            layer_name = m.layers[0].name

        layer = self._set_layer_in_map(m, layer_name)
        layer.datasource = self._create_datasource(collection)

        m.zoom_to_box(bbox or layer.envelope())

        im = Image(width, height)
        render(m, im, 1, 1)

        request.response_content_type = 'image/png'
        return im.tostring('png')
