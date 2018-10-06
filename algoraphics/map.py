import overpass
import pickle
import copy
from shapely.geometry import Polygon
import numpy as np
from .svg import *
from .geom import *
from .color import *
from .map_funs import map_funs


def tag_match(props, key, value=None):
    if key in props:
        if type(value) == list:
            return props[key] in value
        elif props[key] == value or value is None:
            return True
    return False


def get_class(props):
    if tag_match(props, 'landuse') and tag_match(props, 'surface', 'asphalt'):
        return 'asphalt'

    if tag_match(props, 'landuse', 'residential'):
        return 'residential land'
    if tag_match(props, 'landuse', ['farmland', 'farmyard', 'orchard',
                                    'vineyard']):
        return 'farm'
    if tag_match(props, 'landuse', 'forest'):
        return 'forest'
    if tag_match(props, 'landuse', ['grass', 'meadow', 'cemetery']):
        return 'grass'
    if tag_match(props, 'landuse', ['industrial', 'commercial', 'retail']):
        return 'commercial land'
    if tag_match(props, 'landuse'):
        return 'land'

    if tag_match(props, 'building', 'house'):
        return 'house'
    if tag_match(props, 'building', ['residential', 'apartments']):
        return 'residence'
    if tag_match(props, 'building', 'garage'):
        return 'garage'
    if tag_match(props, 'building', ['industrial', 'commercial', 'retail']):
        return 'commercial building'
    if tag_match(props, 'building', ['school', 'church']):
        return 'civic building'
    if tag_match(props, 'building'):
        return 'other building'

    if tag_match(props, 'highway', ['motorway', 'trunk', 'primary',
                                    'secondary', 'tertiary']):
        return 'highway'
    if tag_match(props, 'highway', ['path', 'footway', 'cycleway',
                                    'pedestrian']):
        return 'path'
    if tag_match(props, 'highway'):
        return 'road'

    if tag_match(props, 'natural', 'tree'):
        return 'tree'
    if tag_match(props, 'natural', ['water', 'spring', 'bay']):
        return 'water body'
    if tag_match(props, 'natural', 'wood'):
        return 'forest'
    if tag_match(props, 'natural', 'grassland'):
        return 'grass'
    if tag_match(props, 'natural', ['peak', 'cliff', 'bare rock',
                                    'rock', 'scree', 'ridge']):
        return 'rock'
    if tag_match(props, 'natural', ['sand', 'beach']):
        return 'sand'
    if tag_match(props, 'natural', 'glacier'):
        return 'glacier'

    if tag_match(props, 'waterway'):
        return 'waterway'

    if tag_match(props, 'power', ['line', 'minor_line']):
        return 'power line'
    if tag_match(props, 'power', 'substation'):
        return 'civic building'
    if tag_match(props, 'power'):
        return 'power'

    if tag_match(props, 'wall'):
        return 'barrier'
    if tag_match(props, 'barrier'):
        return 'barrier'

    if tag_match(props, 'amenity', 'restaurant'):
        return 'restaurant'
    if tag_match(props, 'shop'):
        return 'shop'
    if tag_match(props, 'leisure'):
        return 'leisure'

    return 'other'


def acceptable_feature(f):
    # remove unwanted features, e.g. land classifications
    if f['class'] in ['residential land', 'commercial land', 'land']:
        return False
    if f['dim'] == 0 and f['class'] in ['road', 'highway']:
        return False
    return True


def get_features(bbox):
    api = overpass.API()
    map_query = overpass.MapQuery(*bbox)
    response = api.Get(map_query)

    features = []
    for f in response.features:
        feat = dict()
        if 'properties' not in f or len(f['properties']) == 0:
            continue
        props = f['properties']

        feat['class'] = get_class(props)

        feat['coords'] = f['geometry']['coordinates']
        # for point, make list for transforming coordinates later:
        # (points used to be tuples, now lists?)
        # if type(feat['coords']) is tuple:
        if type(feat['coords'][0]) is float:
            feat['coords'] = [feat['coords']]
        feat['coords'] = [tuple(coord) for coord in feat['coords']]

        if f['geometry']['type'] == 'Point':
            feat['dim'] = 0
        elif feat['coords'][0] != feat['coords'][-1] or tag_match(props, 'highway'):
            feat['dim'] = 1
        else:
            feat['dim'] = 2
            del feat['coords'][-1]

        # if feat['dim'] != 0 or feat['class'] != 'other':
        # check blacklist:
        if acceptable_feature(feat):
            features.append(feat)

    return features


def store_features(features, lat, lng, w, h, zoom=18):
    fname = '_'.join([str(lat), str(lng), str(zoom), str(w), str(h)]) + '.p'
    pickle.dump(features, open(fname, 'wb'))

    
def load_features(lat, lng, w, h, zoom=18):
    fname = '_'.join([str(lat), str(lng), str(zoom), str(w), str(h)]) + '.p'
    return pickle.load(open(fname, 'rb'))


def read_config(file_name):
    config = [{}, {}, {}]  # 0D, 1D, 2D
    with open(file_name, 'r') as f:
        for line in f:
            if line[0] != '#':
                dim, feat_class, style = line.strip().split('\t')
                config[int(dim)][feat_class] = style
    return config


class Style:
    def __init__(self, fun, **params):
        # I guess dim isn't needed
        # self.dim = dim  # 0, 1, or 2
        self.fun = fun
        self.params = params

    def render(self, coords):
        return self.fun(coords, **self.params)


def create_style(fun_name, params):
    """Create Style object from function name and list of param values
    (excluding coords)."""
    args = {}
    fun = map_funs[fun_name]['fun']
    for i, val in enumerate(params):
        if type(val) == list:   # color
            if len(val) == 1:
                val = val[0]
            else:
                val = [hex_to_hsl(c) for c in val]
                val = lambda c1=val[0], c2=val[1]: hsl_to_rgb(color_mixture(c1, c2, np.random.random(), mode='hsl'))
                # val = [hex_to_rgb(c) for c in val]
                # val = lambda c1=val[0], c2=val[1]: color_mixture(c1, c2, np.random.random(), mode='rgb')
            # i + 1 to ignore 'coords'
        args[map_funs[fun_name]['params'][i + 1]] = val
    return Style(fun, **args)


def get_map_style(feature, config, styles):
    if feature['class'] in config[feature['dim']]:
        style = config[feature['dim']][feature['class']]
        return styles[style]
    elif 'default' in config[feature['dim']]:
        return styles[config[feature['dim']]['default']]
    else:
        return None


def check_bbox(bbox):
    if bbox[2] - bbox[0] > 0.02:
        raise ValueError("latitude range too high.")
    if bbox[3] - bbox[1] > 0.02:
        raise ValueError("longitude range too high.")
    if bbox[2] < bbox[0]:
        raise ValueError("latitudes switched.")
    if bbox[3] < bbox[1]:
        raise ValueError("longitudes switched.")


def get_map_bbox(lat, lng, width, height, zoom=18):
    """Note: With this method, the zoom is further off closer to the poles, so I just get the lat/lng bounds from leaflet now."""
    tile_w = 256
    lat_per_px = 360 / 2 ** zoom / tile_w
    lng_per_px = lat_per_px / math.cos(rad(lat))
    lat_min = lat - lat_per_px * (height / 2)
    lat_max = lat + lat_per_px * (height / 2)
    lng_min = lng - lng_per_px * (width / 2)
    lng_max = lng + lng_per_px * (width / 2)
    return (lat_min, lng_min, lat_max, lng_max)


def geo_to_image_coords(features, bbox, width, height, zoom=18):
    # bbox = get_map_bbox(lat, lng, width, height, zoom)
    scale_w = width / (bbox[3] - bbox[1])
    scale_h = height / (bbox[2] - bbox[0])
    for f in features:
        translate_points(f['coords'], -bbox[1], -bbox[0])
        scale_points(f['coords'], scale_w, scale_h)


def trim_features_to_canvas(features, width, height, margin=50):
    """Remove area outside the canvas from a polygon.

    This is mainly for mapping where huge land area features would
    waste a lot of computation. The margin is fairly large by default
    to avoid evidence of truncation in generated patterns.

    Args:
        points (list): list of polygon vertices.
        width (number): width of canvas
        height (number): height of canvas
        margin (int): width of margin to include to avoid edge artifacts.

    """
    pts = [(-margin, -margin),
           (-margin, height + margin),
           (width + margin, height + margin),
           (width + margin, -margin)]
    canvas = Polygon(pts)

    # first split features with invalid polygons
    for i in reversed(range(len(features))):
        if features[i]['dim'] == 2:
            feat = features[i]
            poly = Polygon(feat['coords'])
            split_feats = poly.buffer(0)
            if split_feats.geom_type == 'MultiPolygon':
                ls = LineString(poly.exterior.coords)
                mls = unary_union(ls)
                del features[i]
                for x in polygonize(mls):
                    new_feat = copy.deepcopy(feat)
                    new_feat['coords'] = list(x.exterior.coords[:-1])
                    features.insert(i, new_feat)

    # truncate and split features that become disjoint
    for i in reversed(range(len(features))):
        if features[i]['dim'] == 2:
            feat = features[i]
            poly = Polygon(feat['coords'])
            intersect = poly.intersection(canvas)
            if intersect.geom_type in ['GeometryCollection', 'MultiPolygon']:
                del features[i]
                for x in intersect:
                    new_feat = copy.deepcopy(feat)
                    new_feat['coords'] = list(x.exterior.coords)[:-1]
                    features.insert(i, new_feat)
            else:
                feat['coords'] = list(intersect.exterior.coords)[:-1]


def render_map(features, config, styles, width, height):
    features = sorted(features, key=lambda x: -x['dim'])
    trim_features_to_canvas(features, width, height)

    x = []
    for f in features:
        style = get_map_style(f, config, styles)
        if style is not None:
            x.append(style.render(f['coords']))

    if 'background' in config[2]:
        style = config[2]['background']
        margin = 10
        bg = [(-margin, -margin),
              (-margin, height + margin),
              (width + margin, height + margin),
              (width + margin, -margin)]
        x.insert(0, styles[style].render(bg))

    return x

# def render(lat, lng, config, styles, width, height, file, frame_fun=None, optimize=True):
#     # check_bbox(bbox)
#     bbox = get_map_bbox(lat, lng, width, height)
#     # lat to long ratio changes across latitudes:
#     scale_factor = 1 / abs(math.cos(rad(lat))

#     features = get_features(bbox)
#     x = []
#     for f in features:
    
#                            style = get_map_style(f, config, styles)
#         if style is not None:
#             x.append(style.render(f['coords']))

#     # order objects

#     # height = scale_factor * width * (bbox[2] - bbox[0]) / (bbox[3] - bbox[1])
#     if 'background' in config[2]:
#         style = config[2]['background']
#         margin = 10
#         bg = [(-margin, -margin),
#               (-margin, height + margin),
#               (width + margin, height + margin),
#               (width + margin, -margin)]
#         x.insert(0, styles[style].render(bg))

#     if frame_fun is not None:
#         x = frame_fun(x, width, height)

#     write_SVG(x, width, height, file, optimize)
