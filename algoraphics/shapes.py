"""
shapes.py
=========
Create and manipulate shapes.

"""


import numpy as np
import copy
from PIL import Image
from shapely.geometry import Polygon, GeometryCollection
from shapely.geometry import Point as SPoint
from typing import Sequence, Tuple, Union, List, Callable

from .geom import (
    translated_point,
    rotated_point,
    scale_points,
    scaled_point,
    endpoint,
    rad,
    jitter_points,
    interpolate,
)
from .param import fixed_value, Param
from .color import Color

Number = Union[int, float]
Point = Tuple[Number, Number]
Bounds = Tuple[Number, Number, Number, Number]
Collection = Union[list, dict]


def polygon(points: Sequence[Point], **style) -> dict:
    """Create a polygon shape.

    Args:
        points: A list of polygon vertices.

    Returns:
        A polygon shape.

    """
    shape = dict(type="polygon", points=points)
    for key, value in style.items():
        set_style(shape, key, value)
    return shape


def spline(
    points: Sequence[Point], smoothing: Number = 0.2, circular: bool = False, **style
) -> dict:
    """Create a spline shape.

    Args:
        points: A list of points.
        smoothing: The distance to the control point relative to the
          distance to the adjacent point. Usually between zero and
          one.
        circular: If False, spline ends reasonably at the first and
          last points.  If True, the ends of the spline will connect
          smoothly.
    Returns:
        A spline shape.

    """
    shape = dict(type="spline", points=points, smoothing=smoothing, circular=circular)
    for key, value in style.items():
        set_style(shape, key, value)
    return shape


def line(
    p1: Point = None, p2: Point = None, points: Sequence[Point] = None, **style
) -> dict:
    """Create a line or polyline shape.

    Supply either ``p1`` and ``p2`` for a line or ``points`` for a polyline.

    Args:
        p1: The starting point.
        p2: The ending point.
        points: If a list of points is provided, a polyline is created.

    Returns:
        A line or polyline shape.

    """
    if points is not None:
        shape = dict(type="polyline", points=points)
    else:
        p1 = (fixed_value(p1[0]), fixed_value(p1[1]))
        p2 = (fixed_value(p2[0]), fixed_value(p2[1]))
        shape = dict(type="line", p1=p1, p2=p2)
    for key, value in style.items():
        set_style(shape, key, value)
    return shape


def rectangle(
    start: Point = None,
    w: Number = None,
    h: Number = None,
    bounds: Bounds = None,
    **style
) -> dict:
    """Create a rectangular polygon shape.

    Provide either start + w + h or a bounds tuple.

    Args:
        start: Bottom left point of the rectangle (unless w or h is negative).
        w: Width of the rectangle.
        h: Height of the rectangle.
        bounds: The (x_min, y_min, x_max, y_max) of the rectangle.

    Returns:
        A polygon shape.

    """
    if start is not None:
        start = (fixed_value(start[0]), fixed_value(start[1]))
    w = fixed_value(w)
    h = fixed_value(h)
    if bounds is not None:
        bounds = tuple([fixed_value(b) for b in bounds])

    if start is not None:
        assert w is not None and h is not None
        pts = [
            start,
            (start[0] + w, start[1]),
            (start[0] + w, start[1] + h),
            (start[0], start[1] + h),
        ]
    else:
        pts = [
            (bounds[0], bounds[1]),
            (bounds[2], bounds[1]),
            (bounds[2], bounds[3]),
            (bounds[0], bounds[3]),
        ]
    shape = dict(type="polygon", points=pts)
    for key, value in style.items():
        set_style(shape, key, value)
    return shape


def circle(c: Point, r: Number, **style) -> dict:
    """Create a circle shape.

    Args:
        c: The circle's center.
        r: The circle's radius.

    Returns:
        A circle shape.

    """
    c = (fixed_value(c[0]), fixed_value(c[1]))
    r = fixed_value(r)
    shape = dict(type="circle", c=c, r=r)
    for key, value in style.items():
        set_style(shape, key, value)
    return shape


def set_style(
    obj: Collection, attribute: str, value: Union[str, Number, Param, Color, Callable]
):
    """Set style attribute of one or more shapes.

    Args:
        obj: A shape or (nested) list of shapes.
        attribute: Name of the style attribute.
        value: Either a single value, Color, Param, or a function that
          returns values when called with no arguments.

    """
    if isinstance(obj, list):
        for o in obj:
            set_style(o, attribute, value)
    else:
        if "style" not in obj:
            obj["style"] = dict()
        if isinstance(value, Param):
            obj["style"][attribute] = value.value()
        elif type(value) is Color:
            obj["style"][attribute] = value.hex()
        elif callable(value):
            obj["style"][attribute] = value()
        else:
            obj["style"][attribute] = value


def bounding_box(shapes: Collection) -> Bounds:
    """Find the bounding box of a shape or shape collection.

    Args:
        shapes: One or more shapes.

    Returns:
        The min x, max x, min y, and max y coordinates of the input.

    """
    if type(shapes) is list:
        b = list(zip(*[bounding_box(s) for s in shapes]))
        return (min(b[0]), min(b[1]), max(b[2]), max(b[3]))

    elif shapes["type"] == "group":
        if "clip" in shapes:
            return bounding_box(shapes["clip"])
        else:
            return bounding_box(shapes["members"])

    elif "points" in shapes:
        x = [p[0] for p in shapes["points"]]
        y = [p[1] for p in shapes["points"]]
        return (min(x), min(y), max(x), max(y))

    elif shapes["type"] == "circle":
        c, r = shapes["c"], shapes["r"]
        return (c[0] - r, c[1] - r, c[0] + r, c[1] + r)


def rotated_bounding_box(shapes: Collection, angle: Number) -> Bounds:
    """Find the rotated bounding box of a shape or shape collection.

    Args:
        shapes: One or more shapes.
        angle: The orientation of the bounding box in degrees.

    Returns:
        The min x, max x, min y, and max y coordinates in rotated
        space.  Anything created using these coordinates must then be
        rotated by the same angle around the origin to be in the right
        place.

    """
    shapes = copy.deepcopy(shapes)
    rotate_shapes(shapes, -1 * angle)
    return bounding_box(shapes)


def translate_shapes(shapes: Collection, dx: Number, dy: Number):
    """Shift the location of one or more shapes.

    Args:
        shapes: One or more shapes.
        dx: The horizontal shift.
        dy: The vertical shift.

    """
    if isinstance(shapes, list):
        for shape in shapes:
            translate_shapes(shape, dx, dy)
    elif shapes["type"] == "group":
        translate_shapes(shapes["members"], dx, dy)
        if "clip" in shapes:
            translate_shapes(shapes["clip"], dx, dy)
    elif "points" in shapes:
        pts = shapes["points"]
        for i in range(len(pts)):
            pts[i] = translated_point(pts[i], dx, dy)
    elif shapes["type"] == "circle":
        shapes["c"] = translated_point(shapes["c"], dx, dy)
    elif shapes["type"] == "line":
        shapes["p1"] = translated_point(shapes["p1"], dx, dy)
        shapes["p2"] = translated_point(shapes["p2"], dx, dy)
    elif shapes["type"] == "text":
        shapes["x"] += dx
        shapes["y"] += dy
    elif shapes["type"] == "raster":
        shapes["x"] += dx
        shapes["y"] += dy


def rotate_shapes(shapes: Collection, angle: Number, pivot: Point = (0, 0)):
    """Rotate one or more shapes around a point.

    Args:
        shapes: One or more shapes.
        angle: The angle of rotation in degrees.
        pivot: The rotation pivot point.

    """
    if isinstance(shapes, list):
        for shape in shapes:
            rotate_shapes(shape, angle, pivot)
    elif shapes["type"] == "group":
        rotate_shapes(shapes["members"], angle, pivot)
        if "clip" in shapes:
            rotate_shapes(shapes["clip"], angle, pivot)
    elif "points" in shapes:
        pts = shapes["points"]
        for i in range(len(pts)):
            pts[i] = rotated_point(pts[i], pivot, rad(angle))
    elif shapes["type"] == "circle":
        shapes["c"] = rotated_point(shapes["c"], pivot, rad(angle))
    elif shapes["type"] == "line":
        shapes["p1"] = rotated_point(shapes["p1"], pivot, rad(angle))
        shapes["p2"] = rotated_point(shapes["p2"], pivot, rad(angle))


def scale_shapes(shapes: Collection, cx: Number, cy: Number = None):
    """Scale one or more shapes.

    Args:
        shapes: One or more shapes.
        cx: The horizontal scaling factor.
        cy: The vertical scaling factor.  If missing, ``cx`` will be used.

    """
    cy = cx if cy is None else cy
    if isinstance(shapes, list):
        for shape in shapes:
            scale_shapes(shape, cx, cy)
    elif shapes["type"] == "group":
        scale_shapes(shapes["members"], cx, cy)
        if "clip" in shapes:
            scale_shapes(shapes["clip"], cx, cy)
    elif "points" in shapes:
        scale_points(shapes["points"], cx, cy)
    elif shapes["type"] == "circle":
        shapes["c"] = scaled_point(shapes["c"], cx, cy)
        shapes["r"] *= abs(cx)
    elif shapes["type"] == "line":
        shapes["p1"] = scaled_point(shapes["p1"], cx, cy)
        shapes["p2"] = scaled_point(shapes["p2"], cx, cy)
    elif shapes["type"] == "text":
        shapes["x"] *= cx
        shapes["y"] *= cy
    elif shapes["type"] == "raster":
        # note: image contents not scaled/flipped!
        shapes["x"] *= cx
        shapes["y"] *= cy
        # for now I only flip image, no actual scaling
        # shapes['w'] *= abs(cx)
        # shapes['h'] *= abs(cy)

        if cx < 0:
            shapes["image"] = shapes["image"].transpose(Image.FLIP_LEFT_RIGHT)
            if "w" not in shapes:
                shapes["w"] = shapes["image"].width
            shapes["x"] -= shapes["w"]
        if cy < 0:
            shapes["image"] = shapes["image"].transpose(Image.FLIP_TOP_BOTTOM)
            if "h" not in shapes:
                shapes["h"] = shapes["image"].height
            shapes["y"] -= shapes["h"]


def reposition(
    shapes: Collection, position: Point, h_align: str = "left", v_align: str = "bottom"
):
    """Align one or more shapes to a reference point.

    Args:
        shapes: One or more shapes.
        poisition: The reference point.
        h_align: 'left' to move left bound to reference point.
          'center' to horizontally center object around reference
          point.  'right' to move right bound to reference point.
        v_align: 'bottom' to move lower bound to reference point.
          'middle' to vertically center object around reference point.
          'top' to move upper bound to reference point.

    """
    x_min, y_min, x_max, y_max = bounding_box(shapes)

    if h_align == "left":
        dx = position[0] - x_min
    elif h_align == "center":
        dx = position[0] - np.mean([x_min, x_max])
    elif h_align == "right":
        dx = position[0] - x_max

    if v_align == "bottom":
        dy = position[1] - y_min
    elif v_align == "middle":
        dy = position[1] - np.mean([y_min, y_max])
    elif v_align == "top":
        dy = position[1] - y_max

    translate_shapes(shapes, dx, dy)


def coverage(obj: Collection) -> Union[Polygon, SPoint, GeometryCollection]:
    """Create a shapely object.

    Used to calculate area/coverage.

    Args:
        obj: One or more shapes.

    Returns:
        A shapely object representing the union of coverage for all
        input shapes.

    """
    if isinstance(obj, list):
        cover = coverage(obj[0])
        for o in obj[1:]:
            cover = cover.union(coverage(o))
        return coverage
    elif "points" in obj:
        return Polygon(obj["points"])
    elif obj["type"] == "circle":
        return SPoint(obj["c"][0], obj["c"][1]).buffer(obj["r"])
    else:
        print("Can't get coverage for:", obj["type"])


def keep_shapes_inside(shapes: Sequence[Collection], boundary: Collection):
    """Remove shapes if they lie entirely outside the boundary.

    Used to optimize SVG file without altering the appearance.

    Args:
        shapes: A list of shapes, which can be nested.
        boundary: One or more shapes giving the boundary.

    """
    # Reverse so deleting items doesn't affect loop:
    for i, shape in reversed(list(enumerate(shapes))):
        if isinstance(shape, list):
            keep_shapes_inside(shape, boundary)
        elif shape["type"] == "group":
            if "clip" in shape:
                boundary = shape["clip"]
            keep_shapes_inside(shape["members"], boundary)
        else:
            if not coverage(boundary).intersects(coverage(shape)):
                del shapes[i]


def centroid(shape: dict) -> Point:
    """Find the centroid of a shape.

    Args:
        shape: A shape.

    Returns:
        A point.

    """
    if "points" in shape:
        return Polygon(shape["points"]).centroid.coords[0]
    elif shape["type"] == "circle":
        return shape["c"]


def polygon_area(vertices: Sequence[Point]) -> float:
    """Find the area of a polygon.

    Args:
        vertices: The vertex points.

    Returns:
        The area.

    """
    return Polygon(vertices).area


def sample_points_in_shape(shape: dict, n: int) -> List[Point]:
    """Sample random points inside a shape.

    Args:
        shape: A shape (currently works for polygons and splines).
        n: Number of points to sample.

    Returns:
        The sampled points.

    """
    bound = bounding_box(shape)
    points = []
    for i in range(n):
        while True:
            p = (
                np.random.uniform(bound[0], bound[2]),
                np.random.uniform(bound[1], bound[3]),
            )
            if SPoint(p[0], p[1]).within(Polygon(shape["points"])):
                points.append(p)
                break
    return points


def keep_points_inside(points: Sequence[Point], boundary: Collection):
    """Keep points that lie within a boundary.

    Args:
        points: A list of points.
        boundary: One or more shapes giving the boundary.

    """
    # reverse so deleting items doesn't affect loop
    for i, point in reversed(list(enumerate(points))):
        if not coverage(boundary).intersects(SPoint(point)):
            del points[i]


def remove_hidden(shapes: Sequence[Collection]):
    """Remove shapes from (nested) list if they are entirely covered.

    Used to optimize SVG file without altering appearance, e.g. when
    randomly placing objects to fill a region.  Ignores opacity when
    determining overlap.

    Args:
        shapes: A list of shapes.

    """

    def process_list(l, cover):
        for i, item in reversed(list(enumerate(l))):
            if isinstance(item, list):
                process_list(item, cover)
            elif item["type"] == "group":
                if "clip" in item:
                    keep_shapes_inside(item["members"], shapes["clip"])
                process_list(item["members"], cover)
            else:
                shape = coverage(item)
                if shape.within(cover[0]):
                    del l[i]
                else:
                    cover[0] = cover[0].union(shape)

    # Pass list to recursive calls so coverage updates:
    cover = [SPoint((0, 0))]
    # Pack in list because 'shapes' can be single group:
    process_list([shapes], cover)


def wobble(obj: Collection, dev: Number = 2):
    """Add a little messiness to perfect shapes.

    Convert straight lines and curves into slightly wavy splines.

    Args:
        obj: One or more shapes.
        dev: The (approximate) maximum distance a part of an edge will
        move.

    """
    # Note: modify shapes in place, esp. since a single shape might be
    # given.
    if type(obj) is list:
        for x in obj:
            wobble(x, dev)
    elif obj["type"] == "group":
        for x in obj["members"]:
            wobble(x, dev)
    elif obj["type"] == "line":
        _wobble_line(obj, dev)
    elif obj["type"] == "polyline":
        _wobble_polyline(obj, dev)
    elif obj["type"] == "polygon":
        _wobble_polygon(obj, dev)
    elif obj["type"] == "spline":
        if obj["circular"]:
            _wobble_polygon(obj, dev)
        else:
            _wobble_polyline(obj, dev)
    elif obj["type"] == "circle":
        _wobble_circle(obj, dev)


def _wobble_line(obj: dict, dev: Number):
    obj["type"] = "spline"
    pts = [obj["p1"], obj["p2"]]
    del obj["p1"], obj["p2"]
    interpolate(pts, 10)
    jitter_points(pts, dev)
    obj["points"] = pts


def _wobble_polyline(obj: dict, dev: Number):
    obj["type"] = "spline"
    interpolate(obj["points"], 10)
    jitter_points(obj["points"], dev)


def _wobble_polygon(obj: dict, dev: Number):
    obj["type"] = "spline"
    obj["circular"] = True
    pts = obj["points"]
    pts.append(pts[0])
    interpolate(pts, 10)
    del pts[-1]
    jitter_points(pts, dev)


def _wobble_circle(obj: dict, dev: Number):
    r, c = obj["r"], obj["c"]
    del obj["r"], obj["c"]
    obj["type"] = "spline"
    obj["circular"] = True
    n_pts = round(2 * r * np.pi / 10)
    direcs = np.arange(n_pts) / n_pts * 2 * np.pi
    pts = [endpoint(c, direc, r) for direc in direcs]
    jitter_points(pts, dev)
    obj["points"] = pts
