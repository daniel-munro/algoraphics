"""
shapes.py
=========
Create and manipulate shapes.

"""


import numpy as np
import copy
from PIL import Image
from shapely.geometry import Polygon, Point

from .geom import translated_point, rotated_point, scale_points, scaled_point
from .geom import distance, endpoint, rad
from .param import fixed_value, make_param
from .paths import translate_path, rotate_path, scale_path, path_points


def polygon(points):
    """Create a polygon object."""
    return dict(type='polygon', points=points)


def spline(points, curvature=0.3, circular=False):
    """Create a spline object."""
    return dict(type='spline', points=points, curvature=curvature,
                circular=circular)


def line(p1=None, p2=None, points=None):
    """Create a line or polyline object.

    Args:
        p1 (point): The starting point.
        p2 (point): The ending point.
        points (list): If a list of points is provided, a polyline is created.

    Returns:
        dict: A line or polyline shape.

    """
    if points is not None:
        return dict(type='polyline', points=points)
    else:
        p1 = (fixed_value(p1[0]), fixed_value(p1[1]))
        p2 = (fixed_value(p2[0]), fixed_value(p2[1]))
        return dict(type='line', p1=p1, p2=p2)


def rectangle(start=None, w=None, h=None, bounds=None):
    """Create a rectangular polygon object.

    Provide either start + w + h or a bounds tuple.

    Args:
        start (point): Bottom left point of the rectangle (unless w or h is negative).
        w (float|int): Width of the rectangle.
        h (float|int): Height of the rectangle.
        bounds (tuple): The (x_min, x_max, y_min, y_max) of the rectangle.

    Returns:
        dict: A polygon shape.

    """
    if start is not None:
        start = (fixed_value(start[0]), fixed_value(start[1]))
    w = fixed_value(w)
    h = fixed_value(h)
    if bounds is not None:
        bounds = tuple([fixed_value(b) for b in bounds])

    if start is not None:
        assert w is not None and h is not None
        pts = [start,
               (start[0] + w, start[1]),
               (start[0] + w, start[1] + h),
               (start[0], start[1] + h)]
    else:
        pts = [(bounds[0], bounds[2]), (bounds[1], bounds[2]),
               (bounds[1], bounds[3]), (bounds[0], bounds[3])]
    return dict(type='polygon', points=pts)


def circle(c, r):
    """Create a circle object."""
    c = (fixed_value(c[0]), fixed_value(c[1]))
    r = fixed_value(r)
    return dict(type='circle', c=c, r=r)


def wave(start, direction, width, period, length):
    """Generate a wave spline.

    Args:
        start (point): Starting point of the wave.
        direction (float|int): Direction (in degrees) of the wave.
        width (float|int): The total amplitude of the wave from peak to trough.
        period (float|int): Period of the wave.
        length (float|int): End-to-end length of the wave.

    Returns:
        dict: A spline shape.

    """
    start = fixed_value(start)
    direction = fixed_value(direction)
    width = fixed_value(width)
    period = make_param(period)

    points = [endpoint(start, rad(direction + 90), width / 2.)]
    phase = 0
    ref_point = start
    while distance(start, points[-1]) < length:
        phase = (phase + 1) % 2
        ref_point = endpoint(ref_point, rad(direction), period.value() / 2.)
        if phase == 0:
            points.append(endpoint(ref_point, rad(direction + 90), width / 2.))
        else:
            points.append(endpoint(ref_point, rad(direction - 90), width / 2.))
    return spline(points=points)


def bounding_box(shapes):
    """Find bounding box of shape or shape collection.

    Args:
        shapes (dict|list): One or more shapes.

    Returns:
        tuple: The min x, max x, min y, and max y coordinates of the
        input.

    """
    if type(shapes) is list:
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
        return bounding_box(polygon(points=path_points(shapes)))


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
    elif shapes['type'] == 'raster':
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
    elif shapes['type'] == 'raster':
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


def centroid(shape):
    """Find the centroid of a shape.

    Args:
        shape (dict): A shape.

    Returns:
        tuple: A point.

    """
    if 'points' in shape:
        return Polygon(shape['points']).centroid.coords[0]
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
            p = (np.random.uniform(bound[0], bound[1]),
                 np.random.uniform(bound[2], bound[3]))
            if Point(p[0], p[1]).within(Polygon(shape['points'])):
                points.append(p)
                break
    return points


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
