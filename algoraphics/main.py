"""
main.py
=======
General functions for creating graphics.

"""

import random
import numpy as np
from shapely.geometry import Polygon, Point
import copy
from PIL import Image

from .geom import translated_point, rotated_point, scale_points, scaled_point
from .geom import rad, distance
from .paths import rectangle
from .color import Color
from .param import Param


def random_walk(min_val, max_val, max_step, n, start=None):
    """Generate a random walk sequence.

    Steps are sampled from a uniform random distribution.

    Args:
        min_val (float): Values will not fall below this value.
        max_val (float): Values will not fall above this value.
        max_step (flot): Maximum magnitude of each step.
        n (int): Length of the sequence.
        start (number): The starting value.

    Returns:
        list: The generated sequence.

    """
    if start is None:
        x = [random.uniform(min_val, max_val)]
    else:
        x = [float(start)]
    for i in range(1, n):
        val = x[-1] + random.uniform(-max_step, max_step)
        x.append(max(min_val, min(max_val, val)))
    return x


def shuffled(items):
    """Create shuffled version of a list.

    Args:
        items (list): A list of items.

    Returns:
        list: A new list with same objects as input but reordered.

    """
    return random.sample(items, len(items))


def arith_seq(start, stop, length):
    """Generate an arithmetic sequence.

    Args:
        start (float): The first value in the sequence.
        stop (float): The last value in the sequence.
        length (int): The length of the the sequence.

    Returns:
        list: The generated sequence.

    """
    return [(float(x) / (length - 1)) * (stop - start) + start for x
            in range(length)]


def geom_seq(start, stop, length):
    """Generate geometric sequence.

    Args:
        start (float): The first value in the sequence.
        stop (float): The last value in the sequence.
        length (int): Length of the sequence.

    Returns:
        list: The generated sequence.

    """
    r = (float(stop) / start) ** (1. / (length - 1))
    return [start * (r ** i) for i in range(length)]


# # now bounding box will operate on shapes
# def bounding_box(points):
#     points = flatten(points)
#     x = [p[0] for p in points]
#     y = [p[1] for p in points]
#     return min(x), max(x), min(y), max(y)

def bounding_box(shapes):
    """Find bounding box of shape or shape collection.

    Args:
        shapes (dict|list): One or more shapes.

    Returns:
        tuple: The min x, max x, min y, and max y coordinates of the
        input.

    """
    if isinstance(shapes, list):
        b = list(zip(*[bounding_box(s) for s in shapes]))
        return (min(b[0]), max(b[1]), min(b[2]), max(b[3]))

    elif shapes['type'] == 'group':
        if 'clip' in shapes:
            return bounding_box(shapes['clip'])
        else:
            return bounding_box(shapes['members'])

    elif 'points' in shapes:
        x = [p[0] for p in shapes['points']]
        y = [p[1] for p in shapes['points']]
        return min(x), max(x), min(y), max(y)

    elif shapes['type'] == 'circle':
        c, r = shapes['c'], shapes['r']
        return (c[0] - r, c[0] + r, c[1] - r, c[1] + r)

    elif shapes['type'] == 'path':
        return bounding_box(dict(type='polygon', points=path_points(shapes)))


def rotated_bounding_box(shapes, angle):
    """Find the rotated bounding box of a shape or shape collection.

    Args:
        shapes (dict|list): One or more shapes.
        angle (float|int): The orientation of the bounding box in degrees.

    Returns:
        tuple: The min x, max x, min y, and max y coordinates in
        rotated space.  Anything created using these coordinates must
        then be rotated by the same angle around the origin to be in
        the right place.

    """
    shapes = copy.deepcopy(shapes)
    rotate_shapes(shapes, -1 * angle)
    return bounding_box(shapes)


def add_margin(bounds, margin):
    """Add margin to bounds.

    A convenience function used when generating objects to avoid
    issues at the edges of the region or canvas.

    Args:
        bounds (tuple): A tuple of min x, max x, min y, and max y.
        margin (float|int): The width of the margin.

    Returns:
        tuple: Bounds that include the margin on all sides.

    """
    return (bounds[0] - margin, bounds[1] + margin,
            bounds[2] - margin, bounds[3] + margin)


def translate_shapes(shapes, dx, dy):
    """Shift the location of one or more shapes.

    Args:
        shapes (list|dict): One or more shapes.
        dx (float|int): Horizontal shift.
        dy (float|int): Vertical shift.

    """
    if isinstance(shapes, list):
        for shape in shapes:
            translate_shapes(shape, dx, dy)
    elif shapes['type'] == 'group':
        translate_shapes(shapes['members'], dx, dy)
        if 'clip' in shapes:
            translate_shapes(shapes['clip'], dx, dy)
    elif 'points' in shapes:
        pts = shapes['points']
        for i in range(len(pts)):
            pts[i] = translated_point(pts[i], dx, dy)
    elif shapes['type'] == 'circle':
        shapes['c'] = translated_point(shapes['c'], dx, dy)
    elif shapes['type'] == 'line':
        shapes['p1'] = translated_point(shapes['p1'], dx, dy)
        shapes['p2'] = translated_point(shapes['p2'], dx, dy)
    elif shapes['type'] == 'path':
        translate_path(shapes['d'], dx, dy)
    elif shapes['type'] == 'text':
        shapes['x'] += dx
        shapes['y'] += dy
    elif shapes['type'] == 'image':
        shapes['x'] += dx
        shapes['y'] += dy


def rotate_shapes(shapes, angle, pivot=(0, 0)):
    """Rotate one or more shapes around a point.

    Args:
        shapes (dict|list): One or more shapes.
        angle (float|int): The angle of rotation in degrees.
        pivot (tuple): The rotation pivot point.

    """
    if isinstance(shapes, list):
        for shape in shapes:
            rotate_shapes(shape, angle, pivot)
    elif shapes['type'] == 'group':
        rotate_shapes(shapes['members'], angle, pivot)
        if 'clip' in shapes:
            rotate_shapes(shapes['clip'], angle, pivot)
    elif 'points' in shapes:
        pts = shapes['points']
        for i in range(len(pts)):
            pts[i] = rotated_point(pts[i], pivot, rad(angle))
    elif shapes['type'] == 'circle':
        shapes['c'] = rotated_point(shapes['c'], pivot, rad(angle))
    elif shapes['type'] == 'line':
        shapes['p1'] = rotated_point(shapes['p1'], pivot, rad(angle))
        shapes['p2'] = rotated_point(shapes['p2'], pivot, rad(angle))
    elif shapes['type'] == 'path':
        # if 'transform' not in shapes:
        #     shapes['transform'] = ''
        # shapes['transform'] = 'rotate(' + ' '.join([str(angle), str(pivot[0]), str(pivot[1])]) + ') ' + shapes['transform']
        rotate_path(shapes['d'], angle, pivot)


def scale_shapes(shapes, cx, cy=None):
    cy = cx if cy is None else cy
    if isinstance(shapes, list):
        for shape in shapes:
            scale_shapes(shape, cx, cy)
    elif shapes['type'] == 'group':
        scale_shapes(shapes['members'], cx, cy)
        if 'clip' in shapes:
            scale_shapes(shapes['clip'], cx, cy)
    elif 'points' in shapes:
        scale_points(shapes['points'], cx, cy)
    elif shapes['type'] == 'circle':
        shapes['c'] = scaled_point(shapes['c'], cx, cy)
        shapes['r'] *= abs(cx)
    elif shapes['type'] == 'line':
        shapes['p1'] = scaled_point(shapes['p1'], cx, cy)
        shapes['p2'] = scaled_point(shapes['p2'], cx, cy)
    elif shapes['type'] == 'path':
        scale_path(shapes['d'], cx, cy)
    elif shapes['type'] == 'text':
        shapes['x'] *= cx
        shapes['y'] *= cy
    elif shapes['type'] == 'image':
        # note: image contents not scaled/flipped!
        shapes['x'] *= cx
        shapes['y'] *= cy
        # for now I only flip image, no actual scaling
        # shapes['w'] *= abs(cx)
        # shapes['h'] *= abs(cy)

        if cx < 0:
            shapes['image'] = shapes['image'].transpose(Image.FLIP_LEFT_RIGHT)
            if 'w' not in shapes:
                shapes['w'] = shapes['image'].width
            shapes['x'] -= shapes['w']
        if cy < 0:
            shapes['image'] = shapes['image'].transpose(Image.FLIP_TOP_BOTTOM)
            if 'h' not in shapes:
                shapes['h'] = shapes['image'].height
            shapes['y'] -= shapes['h']


def translate_path(path, dx, dy):
    for comp in path:
        if comp['command'] in ['M', 'L', 'A']:
            comp['to'] = translated_point(comp['to'], dx, dy)
        elif comp['command'] == 'C':
            comp['c1'] = translated_point(comp['c1'], dx, dy)
            comp['c2'] = translated_point(comp['c2'], dx, dy)
            comp['to'] = translated_point(comp['to'], dx, dy)


def rotate_path(path, angle, pivot=(0, 0)):
    for comp in path:
        if comp['command'] in ['M', 'L']:
            comp['to'] = rotated_point(comp['to'], pivot, rad(angle))
        elif comp['command'] == 'C':
            comp['c1'] = rotated_point(comp['c1'], pivot, rad(angle))
            comp['c2'] = rotated_point(comp['c2'], pivot, rad(angle))
            comp['to'] = rotated_point(comp['to'], pivot, rad(angle))
        elif comp['command'] == 'A':
            # for now I'm using a single r instead of rx and ry
            # if comp['rx'] != comp['ry']:
                # comp['rotation'] = (comp['rotation'] + angle) % 360
            comp['to'] = rotated_point(comp['to'], pivot, rad(angle))


def scale_path(path, cx, cy=None):
    """Resize path by a factor (radii currently scale by cx)."""
    cy = cx if cy is None else cy
    for comp in path:
        if comp['command'] in ['M', 'L']:
            comp['to'] = scaled_point(comp['to'], cx, cy)
        elif comp['command'] == 'C':
            comp['c1'] = scaled_point(comp['c1'], cx, cy)
            comp['c2'] = scaled_point(comp['c2'], cx, cy)
            comp['to'] = scaled_point(comp['to'], cx, cy)
        elif comp['command'] == 'A':
            comp['r'] *= abs(cx)
            if cx * cy < 0:
                comp['positive'] = not comp['positive']
            comp['to'] = scaled_point(comp['to'], cx, cy)


def reposition(shapes, position, h_align='left', v_align='bottom'):
    """Align one or more shapes to a reference point.

    Args:
        shapes (dict|list): One or more shapes.
        poisition (tuple): reference point.
        h_align (str): 'left' to move left bound to reference point.  'center' to horizontally center object around reference point.  'right' to move right bound to reference point.
        v_align (str): 'bottom' to move lower bound to reference point.  'middle' to vertically center object around reference point.  'top' to move upper bound to reference point.

    """
    x_min, x_max, y_min, y_max = bounding_box(shapes)

    if h_align == 'left':
        dx = position[0] - x_min
    elif h_align == 'center':
        dx = position[0] - np.mean([x_min, x_max])
    elif h_align == 'right':
        dx = position[0] - x_max

    if v_align == 'bottom':
        dy = position[1] - y_min
    elif v_align == 'middle':
        dy = position[1] - np.mean([y_min, y_max])
    elif v_align == 'top':
        dy = position[1] - y_max

    translate_shapes(shapes, dx, dy)


def polygon_centroid(vertices):
    """Find the centroid of a polygon.

    Args:
        vertices (list): A list of vertex points.

    Returns:
        tuple: A point.

    """
    return Polygon(vertices).centroid.coords[0]


def centroid(shape):
    """Find the centroid of a shape.

    Args:
        shape (dict): A shape.

    Returns:
        tuple: A point.

    """
    if 'points' in shape:
        return polygon_centroid(shape['points'])
    elif shape['type'] == 'circle':
        return shape['c']


def polygon_area(vertices):
    """Find the area of a polygon.

    Args:
        vertices (list): The vertex points.

    Returns:
        float: The area.

    """
    return Polygon(vertices).area


def sample_points_in_shape(shape, n):
    """Sample random points inside a shape.

    Args:
        shape (dict): A shape (currently works for polygons and splines).
        n (int): Number of points to sample.

    Returns:
        list: The sampled points.

    """
    bound = bounding_box(shape)
    points = []
    for i in range(n):
        while True:
            p = (random.uniform(bound[0], bound[1]),
                 random.uniform(bound[2], bound[3]))
            if Point(p[0], p[1]).within(Polygon(shape['points'])):
                points.append(p)
                break
    return points


def path_points(path):
    """Get skeleton points of path.

    Useful for finding an approximate bounding box for a path.

    """
    pts = []
    for cmd in path['d']:
        if 'to' in cmd:
            pts.append(cmd['to'])
    return pts


def coverage(obj):
    """Create shapely object.

    Used to calculate area/coverage.

    """
    if isinstance(obj, list):
        cover = coverage(obj[0])
        for o in obj[1:]:
            cover = cover.union(coverage(o))
        return coverage
    elif 'points' in obj:
        return Polygon(obj['points'])
    elif obj['type'] == 'path':
        pts = path_points(obj)
        return Polygon(pts)
    elif obj['type'] == 'circle':
        return Point(obj['c'][0], obj['c'][1]).buffer(obj['r'])
    else:
        print("Can't get coverage for:", obj['type'])


def keep_shapes_inside(shapes, boundary):
    """Remove shapes from (nested) list if they lie entirely outside the boundary.

    Used to optimize SVG file without altering appearance.

    Args:
        shapes (list): A list of shapes.
        boundary (dict|list): One or more shapes giving the boundary.

    """
    # Reverse so deleting items doesn't affect loop:
    for i, shape in reversed(list(enumerate(shapes))):
        if isinstance(shape, list):
            keep_shapes_inside(shape, boundary)
        elif shape['type'] == 'group':
            if 'clip' in shape:
                boundary = shape['clip']
            keep_shapes_inside(shape['members'], boundary)
        else:
            if not coverage(boundary).intersects(coverage(shape)):
                del shapes[i]


def keep_points_inside(points, boundary):
    """Keep points that lie within a boundary.

    Args:
        points (list): A list of points.
        boundary (dict|list): One or more shapes giving the boundary.

    """
    # reverse so deleting items doesn't affect loop
    for i, point in reversed(list(enumerate(points))):
        if not coverage(boundary).intersects(Point(point)):
            del points[i]


def remove_hidden(shapes):
    """Remove shapes from (nested) list if they are entirely covered.

    Used to optimize SVG file without altering appearance, e.g. when
    randomly placing objects to fill a region.  Ignores opacity when
    determining overlap.

    Args:
        shapes (list): A list of shapes.

    """
    def process_list(l, cover):
        for i, item in reversed(list(enumerate(l))):
            if isinstance(item, list):
                process_list(item, cover)
            elif item['type'] == 'group':
                if 'clip' in item:
                    keep_shapes_inside(item['members'], shapes['clip'])
                process_list(item['members'], cover)
            else:
                shape = coverage(item)
                if shape.within(cover[0]):
                    del l[i]
                else:
                    cover[0] = cover[0].union(shape)

    # Pass list to recursive calls so coverage updates:
    cover = [Point((0, 0))]
    # Pack in list because 'shapes' can be single group:
    process_list([shapes], cover)


def reorder_objects(objects, by='random', w=None, h=None):
    """Reorder objects in list.

    Used to change order in which objects are drawn.

    Args:
        objects (list): A list whose items are shapes or lists.
        by (str): 'random' to shuffle objects.  'out to in' to arrange objects closer to the center on top of (later in list) those further from the center.  Distance is determined by furthest corner of bounding box so that smaller objects tend to be arranged on top of larger ones that surround them.
        w (float|int): Canvas width, used to get center when by='out to in'.
        h (float|int): Canvas height, used to get center when by='out to in'.

    """
    if by == 'random':
        random.shuffle(objects)

    elif by == 'out to in':
        center = (w / 2., h / 2.)

        def key_fun(obj):
            b = bounding_box(obj)
            # c = ((b[1] + b[0]) / 2., (b[3] + b[2]) / 2.)
            # return distance(center, c)
            d1 = distance(center, (b[0], b[2]))
            d2 = distance(center, (b[0], b[3]))
            d3 = distance(center, (b[1], b[2]))
            d4 = distance(center, (b[1], b[3]))
            return max(d1, d2, d3, d4)
        objects.sort(key=key_fun, reverse=True)


def background(fill, w, h, margin=0):
    """Create a background color for the canvas.

    See region_background to set background for a specific region.

    Args:
        fill (color): The background color.
        w (int): width of canvas.
        h (int): height of canvas.
        margin (int): width of margin to include to avoid edge artifacts.

    Returns:
        tuple: A filled rectangular polygon covering the canvas.

    """
    bg = rectangle(start=(-margin, -margin),
                   w=w + 2 * margin,
                   h=h + 2 * margin)
    set_style(bg, 'fill', fill)
    return bg


def region_background(region, color):
    """Add background color to clipped region.

    Adds a filled rectangle to the beginning of the region's members.

    Args:
        region (dict): A clipped group object.
        color (color|function): A color or function to apply to the region.

    """
    bounds = add_margin(bounding_box(region['clip']), 10)
    bg = rectangle(bounds=bounds)
    set_style(bg, 'fill', color)
    if isinstance(region['members'], list):
        region['members'].insert(0, bg)
    else:
        region['members'] = [bg, region['members']]


def tint_region(region, color, opacity):
    bounds = add_margin(bounding_box(region['clip']), 10)
    tint = rectangle(bounds=bounds)
    set_style(tint, 'fill', color)
    set_style(tint, 'opacity', opacity)
    if isinstance(region['members'], list):
        region['members'].append(tint)
    else:
        region['members'] = [region['members'], tint]


def set_style(obj, attribute, value):
    """Set style attribute of one or more shapes.

    Args:
        obj (dict|list): A shape or (nested) list of shapes.
        attribute (str): Name of the style attribute (replace '-' with '_').
        value (str|number|function): either a single value or a function that returns values when called with no arguments.

    """
    if isinstance(obj, list):
        for o in obj:
            set_style(o, attribute, value)
    else:
        if 'style' not in obj:
            obj['style'] = dict()
        if type(value) is Param:
            obj['style'][attribute] = value.value()
        elif type(value) is Color:
            obj['style'][attribute] = value.hex()
        elif callable(value):
            obj['style'][attribute] = value()
        else:
            obj['style'][attribute] = value


def flatten(objects):
    """Create a flattened list from a nested list.

    Args:
        objects (object): A nested list or a non-list.

    Returns:
        list: The non-list elements within the input.

    """
    out = []
    if isinstance(objects, list):
        for obj in objects:
            out.extend(flatten(obj))
    else:
        out.append(objects)
    return out


def _markov_next(state, trans_probs):
    """Get the next state in a first-order Markov chain.

    Args:
        state (str): The current state.
        trans_probs (dict): A dictionary of dictionaries containing transition probabilities from one state (first key) to another (second key).

    Returns:
        str: The next state.

    """
    states = list(trans_probs[state].keys())
    probs = [trans_probs[state][s] for s in states]
    return np.random.choice(states, p=probs)
