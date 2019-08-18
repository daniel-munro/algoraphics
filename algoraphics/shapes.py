"""
shapes.py
=========
Create and manipulate shapes.

"""


import numpy as np
from copy import deepcopy
from shapely.geometry import GeometryCollection
from shapely.geometry import Polygon as SPolygon
from shapely.geometry import Point as SPoint
from typing import Sequence, Tuple, Union, List

from .geom import (
    rad,
)
from .param import fixed_value, Param, make_param
from .color import Color
from .point import Point, Translation, Rotation, Scaling, make_point

# Number = Union[int, float]
# Point = Tuple[Number, Number]
Pnt = Tuple[float, float]
# Bounds = Tuple[Number, Number, Number, Number]
Bounds = Tuple[float, float, float, float]
Collection = Union[list, "Shape", "Group"]


class Shape:
    def __mul__(self, other):
        return [deepcopy(self) for i in range(other)]

    def __rmul__(self, other):
        return [deepcopy(self) for i in range(other)]


class Polygon(Shape):
    """A polygon shape.

    Args:
        points: A list of polygon vertices.

    """

    def __init__(self, points: Sequence[Point], **style):
        self.points = [make_point(p) for p in points]
        self.style = style


class Spline(Shape):
    """A spline shape.

    Args:
        points: A list of points.
        smoothing: The distance to the control point relative to the
          distance to the adjacent point. Usually between zero and
          one.
        circular: If False, spline ends reasonably at the first and
          last points.  If True, the ends of the spline will connect
          smoothly.

    """

    def __init__(
        self,
        points: Sequence[Point],
        smoothing: float = 0.3,
        circular: bool = False,
        **style
    ):
        self.points = [make_point(p) for p in points]
        self.smoothing = smoothing
        self.circular = circular
        self.style = style


class Line(Shape):
    """A line or polyline shape.

    Supply either ``p1`` and ``p2`` for a line or ``points`` for a
    polyline.

    Args:
        p1: The starting point.
        p2: The ending point.
        points: If a list of points is provided, a polyline is created.

    """

    def __init__(
        self,
        p1: Point = None,
        p2: Point = None,
        points: Sequence[Point] = None,
        **style
    ):
        if points is not None:
            self.points = [make_point(p) for p in points]
        else:
            self.points = [make_point(p1), make_point(p2)]
        self.style = style


class Circle(Shape):
    """A circle shape.

    Args:
        c: The circle's center.
        r: The circle's radius.

    """

    def __init__(self, c: Point, r: float, **style):
        self.c = make_point(c)
        self.r = make_param(r)
        self.style = style


class Group:
    """A group of shapes, usually with a clip.

    Args:
        members: The shapes in the group.
        clip: The shape/s determining where the members are visible.
        filter: An SVG filter, e.g. shadow, to apply to the group.

    """

    def __init__(
        self, members: Collection = None, clip: Collection = None, filter: dict = None
    ):
        self.members = [] if members is None else members
        if type(self.members) is not list:
            self.members = [self.members]
        self.clip = [] if clip is None else clip
        if type(self.clip) is not list:
            self.clip = [self.clip]
        self.filter = filter


def rectangle(
    start: Pnt = None, w: float = None, h: float = None, bounds: Bounds = None, **style
) -> Polygon:
    """Create a rectangular Polygon shape.

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
    return Polygon(points=pts, **style)


def set_style(obj: Collection, attribute: str, value: Union[str, float, Param, Color]):
    """Set style attribute of one or more shapes.

    Args:
        obj: A shape or (nested) list of shapes.
        attribute: Name of the style attribute.
        value: Either a single value, Color, or Param.

    """
    if type(obj) is list:
        for o in obj:
            set_style(o, attribute, value)
    else:
        obj.style[attribute] = value


def set_styles(obj: Collection, attribute: str, value: Union[Param, Color]):
    """Set style attribute of one or more shapes.

    Unlike set_style, it creates a deep copy of the Param or Color for
    each shape so that there is variation.

    Args:
        obj: A shape or (nested) list of shapes.
        attribute: Name of the style attribute.
        value: A Color or Param.

    """
    if type(obj) is list:
        for o in obj:
            set_styles(o, attribute, value)
    else:
        obj.style[attribute] = deepcopy(value)


def bounding_box(shapes: Collection) -> Bounds:
    """Find the bounding box of a shape or shape collection.

    Currently assumes t == 0.

    Args:
        shapes: One or more shapes.

    Returns:
        The min x, max x, min y, and max y coordinates of the input.

    """
    if type(shapes) is list:
        b = list(zip(*[bounding_box(s) for s in shapes]))
        return (min(b[0]), min(b[1]), max(b[2]), max(b[3]))
    elif type(shapes) is Group:
        if len(shapes.clip) > 0:
            return bounding_box(shapes.clip)
        else:
            return bounding_box(shapes.members)
    elif type(shapes) in [Polygon, Spline, Line]:
        x = [p.state()[0] for p in shapes.points]
        y = [p.state()[1] for p in shapes.points]
        return (min(x), min(y), max(x), max(y))
    elif type(shapes) is Circle:
        c, r = shapes.c.state(), shapes.r.state()
        return (c[0] - r, c[1] - r, c[0] + r, c[1] + r)


def rotated_bounding_box(shapes: Collection, angle: float) -> Bounds:
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
    shapes = deepcopy(shapes)
    rotate_shapes(shapes, -1 * angle)
    return bounding_box(shapes)


def translate_shapes(shapes: Collection, dx: float, dy: float):
    """Shift the location of one or more shapes.

    Args:
        shapes: One or more shapes.
        dx: The horizontal shift.
        dy: The vertical shift.

    """
    if type(shapes) is list:
        for shape in shapes:
            translate_shapes(shape, dx, dy)
    elif type(shapes) is Group:
        translate_shapes(shapes.members, dx, dy)
        translate_shapes(shapes.clip, dx, dy)
    elif type(shapes) in [Polygon, Spline, Line]:
        for i in range(len(shapes.points)):
            shapes.points[i] = Translation(shapes.points[i], (dx, dy))
    elif type(shapes) is Circle:
        shapes.c = Translation(shapes.c, (dx, dy))


def rotate_shapes(shapes: Collection, angle: float, pivot: Pnt = (0, 0)):
    """Rotate one or more shapes around a point.

    Args:
        shapes: One or more shapes.
        angle: The angle of rotation in degrees.
        pivot: The rotation pivot point.

    """
    if type(shapes) is list:
        for shape in shapes:
            rotate_shapes(shape, angle, pivot)
    elif type(shapes) is Group:
        rotate_shapes(shapes.members, angle, pivot)
        rotate_shapes(shapes.clip, angle, pivot)
    elif type(shapes) in [Polygon, Spline, Line]:
        for i in range(len(shapes.points)):
            shapes.points[i] = Rotation(shapes.points[i], pivot, rad(angle))
    elif type(shapes) is Circle:
        shapes.c = Rotation(shapes.c, pivot, rad(angle))


def scale_shapes(shapes: Collection, cx: float, cy: float = None):
    """Scale one or more shapes.

    Args:
        shapes: One or more shapes.
        cx: The horizontal scaling factor.
        cy: The vertical scaling factor.  If missing, ``cx`` will be used.

    """
    cy = cx if cy is None else cy
    if type(shapes) is list:
        for shape in shapes:
            scale_shapes(shape, cx, cy)
    elif type(shapes) is Group:
        scale_shapes(shapes.members, cx, cy)
        scale_shapes(shapes.clip, cx, cy)
    elif type(shapes) in [Polygon, Spline, Line]:
        for i in range(len(shapes.points)):
            shapes.points[i] = Scaling(shapes.points[i], cx, cy)
    elif type(shapes) is Circle:
        shapes.c = Scaling(shapes.c, cx, cy)
        shapes.r = shapes.r * abs(cx)


def coverage(obj: Collection) -> Union[SPolygon, SPoint, GeometryCollection]:
    """Create a shapely object.

    Used to calculate area/coverage.

    Args:
        obj: One or more shapes.

    Returns:
        A shapely object representing the union of coverage for all
        input shapes.

    """
    if type(obj) is list:
        cover = coverage(obj[0])
        for o in obj[1:]:
            cover = cover.union(coverage(o))
        return cover
    elif type(obj) in [Polygon, Spline, Line]:
        return SPolygon([pt.state() for pt in obj.points])
    elif type(obj) is Circle:
        c = obj.c.state()
        return SPoint(c[0], c[1]).buffer(obj.r.state())
    else:
        print("Can't get coverage for:", obj)


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
        elif type(shape) is Group:
            if len(shape.clip) > 0:
                boundary = shape.clip
            keep_shapes_inside(shape.members, boundary)
        else:
            if not coverage(boundary).intersects(coverage(shape)):
                del shapes[i]


def centroid(shape: Shape) -> Pnt:
    """Find the centroid of a shape.

    Args:
        shape: A shape.

    Returns:
        A point.

    """
    if type(shape) in [Polygon, Spline, Line]:
        return SPolygon([p.state() for p in shape.points]).centroid.coords[0]
    elif type(shape) is Circle:
        return shape.c


def polygon_area(vertices: Sequence[Pnt]) -> float:
    """Find the area of a polygon.

    Args:
        vertices: The vertex points.

    Returns:
        The area.

    """
    return SPolygon(vertices).area


def sample_points_in_shape(shape: dict, n: int) -> List[Pnt]:
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
            region = SPolygon([pt.state() for pt in shape.points])
            if SPoint(p[0], p[1]).within(region):
                points.append(p)
                break
    return points


def keep_points_inside(points: Sequence[Pnt], boundary: Collection):
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
            elif type(item) is Group:
                if len(item.clip) > 0:
                    keep_shapes_inside(item.members, shapes.clip)
                process_list(item.members, cover)
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
