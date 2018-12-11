"""
geom.py
=======
General functions involving points in 2D space.

"""

import math
import numpy as np
import rtree
from typing import Union, Tuple, Sequence

Number = Union[int, float]
Point = Tuple[Number, Number]


def rad(deg: Number) -> float:
    """Convert degrees to radians."""
    return deg * 2 * math.pi / 360


def deg(rad: Number) -> float:
    """Convert radians to degrees."""
    return rad / (2 * math.pi) * 360


def rand_point_on_circle(c: Point, r: Number) -> Point:
    """Return a random point on a circle.

    Args:
        c: The center.
        r: The radius.

    """
    theta = np.random.uniform(-math.pi, math.pi)
    return (c[0] + math.cos(theta) * r, c[1] + math.sin(theta) * r)


def points_on_line(start: Point, end: Point,
                   spacing: Number) -> Sequence[Point]:
    """Generate points along a line.

    Args:
        start: The first point.
        end: The last point.
        spacing: The approximate (max) distance between adjacent points.

    Returns:
        A list of points.

    """
    n_points = math.ceil(distance(start, end) / spacing) + 1

    dx = float(end[0] - start[0]) / (n_points - 1)
    dy = float(end[1] - start[1]) / (n_points - 1)

    x = [start[0] + i * dx for i in range(n_points)]
    y = [start[1] + i * dy for i in range(n_points)]
    return list(zip(x, y))


def interpolate(points: Sequence[Point], spacing: Number):
    """Insert interpolated points.

    Insert equally-spaced, linearly interpolated points into list such
    that consecutive points are no more than 'spacing' distance apart.

    Args:
        points: A list of points.
        spacing: Maximum distance between adjacent points.

    """
    for i in reversed(range(1, len(points))):
        if distance(points[i - 1], points[i]) > spacing:
            newpts = points_on_line(points[i - 1], points[i], spacing)[1:-1]
            points[i:i] = newpts


def points_on_arc(center: Point, radius: Number, theta_start: Number,
                  theta_end: Number, spacing: Number) -> Sequence[Point]:
    """Generate points along an arc.

    Args:
        center: The center of the arc.
        radius: The radius of the arc.
        theta_start: The starting position in degrees.
        theta_end: The ending position in degrees.
        spacing: The approximate distance between adjacent points.

    Returns:
        A list of points.

    """
    theta_start = rad(theta_start)
    theta_end = rad(theta_end)
    theta = float(theta_end - theta_start)
    n_points = int(abs(theta) * radius / spacing) + 1
    theta_p = [theta_start + i * theta / (n_points - 1) for i in
               range(n_points)]
    return [endpoint(center, t, radius) for t in theta_p]


def endpoint(start: Point, angle: Number, distance: Number) -> Point:
    """
    Args:
        start: Starting point.
        angle: Direction from starting point in radians.
        distance: Distance from starting point.

    Returns:
        A point ``distance`` from ``start`` in the direction ``angle``.

    """
    x = start[0] + math.cos(angle) * distance
    y = start[1] + math.sin(angle) * distance
    return (x, y)


def move_toward(start: Point, target: Point, distance: Number) -> Point:
    """
    Args:
        start: Starting point.
        target: Point to indicate direction from starting point to move.
        distance: Distance from starting point to returned point.

    Returns:
        A point ``distance`` from ``start`` in the direction of ``target``.

    """
    angle = math.atan2(target[1] - start[1], target[0] - start[0])
    return endpoint(start, angle, distance)


def rotate_and_move(start, ref, angle, distance):
    """Combine ``rotated_point`` and ``move_toward`` for convenience.

    Args:
        start: Starting point.
        ref: A reference point.
        angle: The angle to rotate ``ref`` around start.
        distance: The distance to move from ``start``.

    Returns:
        A point ``distance`` from ``start`` in the ``angle`` direction
        relative to ``ref``.

    """
    x = rotated_point(ref, start, angle)
    return move_toward(start, x, distance)


def distance(p1: Point, p2: Point) -> float:
    """Get the distance between two points.

    Args:
        p1: First point.
        p2: Second point.

    """
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    return math.sqrt(dx * dx + dy * dy)


def get_nearest(points: Sequence[Point], point: Point, index: bool =
                False) -> Union[Point, int]:
    """Find the nearest point in a list to a target point.

    Args:
        points: A list of points.
        point: The target point.
        index: Whether to return the point or its index in the list.

    Returns:
        If index is False, returns point, otherwise returns index of
        point in list.

    """
    nearest = 0
    nearest_dist = distance(points[nearest], point)
    for p in range(1, len(points)):
        dist = distance(points[p], point)
        if dist < nearest_dist:
            nearest = p
            nearest_dist = dist
    return nearest if index else points[nearest]


class Rtree:
    """An object to efficiently query a field of points.

    Args:
        points: Starting points.

    """
    def __init__(self, points: Sequence[Point] = None):
        if points is None:
            points = []
        self.idx = rtree.index.Index()
        self.points = []  # for retrieving points, e.g. last N
        self.size = 0
        for p in points:
            self.add_point(p)

    def add_point(self, point: Point):
        """Add a point to the collection.

        Args:
            point: The new point.

        """
        self.idx.add(self.size, point)
        self.points.append(point)
        self.size += 1

    def add_points(self, points: Sequence[Point]):
        """Add points to the collection.

        Args:
            points: The new points.

        """
        for point in points:
            self.add_point(point)

    def nearest(self, point: Point, n: int = 1, index: bool =
                False) -> Union[Sequence[Point], Point]:
        """Get the nearest point or points to a query point.

        Args:
            point: A query point.
            n: Number of nearest points to return.
            index: Whether to return the nearets points' indices
              instead of the points themselves.

        Returns:
            If ``n`` is 1, the nearest point, otherwise a list of
            nearest points.

        """
        a = list(self.idx.nearest(point, n))
        if not index:
            a = [self.points[x] for x in a]
        if n == 1:
            a = a[0]
        return a


def midpoint(p1: Point, p2: Point) -> Point:
    """Get the midpoint between two points.

    Args:
        p1: A point.
        p2: Another point.

    """
    return (p1[0] + p2[0]) / 2., (p1[1] + p2[1]) / 2.


def angle_between(p1: Point, p2: Point, p3: Point) -> float:
    """Get the angle (in radians) between segment p2->p1 and p2->p3.

    The angle can be negative.

    Args:
        p1: The first endpoint.
        p2: The point where the angle is calculated.
        p3: The other endpoint.

    """
    dir1 = math.atan2(p1[1] - p2[1], p1[0] - p2[0])
    dir2 = math.atan2(p3[1] - p2[1], p3[0] - p2[0])
    return dir2 - dir1


def translated_point(point: Point, dx: Number, dy: Number) -> Point:
    """Get a translated point.

    Args:
        point: The starting location.
        dx: The horizontal translation.
        dy: The vertical translation.

    """
    return (point[0] + dx, point[1] + dy)


def rotated_point(point: Point, pivot: Point, angle: Number) -> Point:
    """Get the new location of a point after rotating around a reference point.

    Args:
        point: The starting location.
        pivot: The center of rotation.
        angle: The angle in radians by which to rotate.

    """
    x = (((point[0] - pivot[0]) * math.cos(angle))
         - ((point[1] - pivot[1]) * math.sin(angle))
         + pivot[0])
    y = (((point[1] - pivot[1]) * math.cos(angle))
         + ((point[0] - pivot[0]) * math.sin(angle))
         + pivot[1])
    return (x, y)


def scaled_point(point: Point, cx: Number, cy: Number = None) -> Point:
    """Get the new location of ``point`` after scaling coordinates.

    Provide either one scaling factor or cx and cy.

    Args:
        cx: Either the scaling factor, or if ``cy`` is also provided,
          the horizontal scaling factor.
        cy: The vertical scaling factor.

    """
    cy = cx if cy is None else cy
    return (point[0] * cx, point[1] * cy)


# def in_box(point, x_min, x_max, y_min, y_max):
#     """Determine if a point lies within the specified bounds."""
#     in_bounds = (x_min < point[0] and point[0] < x_max and
#                  y_min < point[1] and point[1] < y_max)
#     return in_bounds


# def in_ellipse(point, x_min, x_max, y_min, y_max):
#     """Determine if a point lies within an ellipse with the specified bounds."""
#     c = (x_min + x_max) / 2., (y_min + y_max) / 2.
#     r_x = c[0] - x_min
#     r_y = c[1] - y_min
#     return ((point[0] - c[0]) / r_x) ** 2 + ((point[1] - c[1]) / r_y) ** 2 < 1


def horizontal_range(points: Sequence[Point]) -> Number:
    """Get the magnitude of the horizontal range of a list of points.

    Args:
        points: A list of points.

    """
    if len(points) == 0:
        return 0
    else:
        return max([x[0] for x in points]) - min([x[0] for x in points])


def translate_points(points: Sequence[Union[Point, Sequence]], dx:
                     Number, dy: Number):
    """Shift the location of points.

    Args:
        points: A list of points, which can be nested.
        dx: Horizontal change.
        dy: Vertical change.

    """
    for i in range(len(points)):
        if isinstance(points[i], list):
            translate_points(points[i], dx, dy)
        else:
            points[i] = translated_point(points[i], dx, dy)


def scale_points(points: Sequence[Union[Point, Sequence]], cx: Number,
                 cy: Number = None):
    """Scale the coordinates of points.

    Args:
        points: A list of points, which can be nested.
        cx: The horizontal scale factor.
        cy: The vertical scale factor. If omitted, y-coordinates will
          be scaled by cx.

    """
    for i in range(len(points)):
        if isinstance(points[i], list):
            scale_points(points[i], cx, cy)
        else:
            points[i] = scaled_point(points[i], cx, cy)


def jitter_points(points: Sequence[Point], deviation: Number, type: str):
    """Add noise to the locations of points.

    Args:
        points: A list of points.
        deviation: For gaussian jitter, the standard deviation. For
          uniform jitter, the maximum distance.
        type: The type of noise, 'gaussian' or 'uniform'.

    """
    for i in range(len(points)):
        angle = np.random.uniform(0, 2 * math.pi)
        if type == 'gaussian':
            dist = np.random.normal(0, deviation)
        elif type == 'uniform':
            dist = np.random.uniform(0, deviation)
        points[i] = endpoint(points[i], angle, dist)


def jittered_points(points: Sequence[Point], deviation: Number, type:
                    str) -> Sequence[Point]:
    """Get noisy copy of points.

    Like jitter_points but returns jittered points, not affecting the
    original list.

    Args:
        points: A list of points.
        deviation: For gaussian jitter, the standard deviation. For
          uniform jitter, the maximum distance.
        type: The type of noise, 'gaussian' or 'uniform'.

    """
    x = points[:]
    jitter_points(x, deviation, type)
    return x


def line_to_polygon(points: Sequence[Point], width: Number) -> Sequence[Point]:
    """Convert a sequence of points to a path outline.

    Imagining the points were connected with a stroke with positive
    width, the outline of the stroke is returned.

    Args:
        points: A list of line points.
        width: Width of the path to be outlined.

    Returns:
        A list of points.

    """

    pts = []
    end1 = rotate_and_move(points[0], points[1], -math.pi / 2, width / 2)
    end2 = rotate_and_move(points[-1], points[-2], math.pi / 2, width / 2)
    end3 = rotate_and_move(points[-1], points[-2], -math.pi / 2, width / 2)
    end4 = rotate_and_move(points[0], points[1], math.pi / 2, width / 2)
    pts.append(end1)
    for i in range(1, len(points) - 1):
        angle = angle_between(points[i - 1], points[i], points[i + 1])
        if angle > rad(10) or angle < -rad(10):
            dist = (width / 2) / math.sin(angle / 2)
        else:
            print(angle)
            dist = 0
        p1 = rotate_and_move(points[i], points[i - 1], angle / 2, dist)
        pts.append(p1)
    pts.extend([end2, end3])
    for i in reversed(range(1, len(points) - 1)):
        pts.append(rotated_point(pts[i], points[i], math.pi))
    pts.append(end4)
    return pts


def is_clockwise(points: Sequence[Point]) -> bool:
    """Determine the derection of a sequence of points around a polygon.

    Finds whether a set of polygon points goes in a clockwise or
    counterclockwise direction.  If edges cross, it gives the more
    prominent direction.

    Args:
        points: A list of polygon vertices.

    """
    p = points + [points[0]]
    edge_vals = [(p[i+1][0] - p[i][0]) * (p[i+1][1] + p[i][1]) for i
                 in range(len(points))]
    return sum(edge_vals) > 0
