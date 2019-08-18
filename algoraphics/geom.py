"""
geom.py
=======
General functions involving points in 2D space.

"""

import math
import numpy as np
from typing import Union, Tuple, Sequence

# Number = Union[int, float]
# Point = Tuple[Number, Number]
Pnt = Tuple[float, float]


def rad(deg: float) -> float:
    """Convert degrees to radians."""
    return deg * 2 * math.pi / 360


def deg(rad: float) -> float:
    """Convert radians to degrees."""
    return rad / (2 * math.pi) * 360


def points_on_line(start: Pnt, end: Pnt, spacing: float) -> Sequence[Pnt]:
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


def interpolate(points: Sequence[Pnt], spacing: float):
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


def remove_close_points(points: Sequence[Pnt], spacing: float):
    """Remove points that are closer than 'spacing'.

    A point is removed if it follows the previous point too closely.
    Consecutive points cannot both be removed, so the list is scanned
    repeatedly until all consecutive points are at least 'spacing'
    apart.

    Args:
        points: A list of points.
        spacing: Minimum distance between adjacent points.

    """
    any_too_close = True
    while any_too_close:
        any_too_close = False
        del_last = False
        for i in reversed(range(1, len(points))):
            if distance(points[i-1], points[i]) < spacing and not del_last:
                del points[i]
                any_too_close = True
                del_last = True
            else:
                del_last = False


def points_on_arc(
    center: Pnt,
    radius: float,
    theta_start: float,
    theta_end: float,
    spacing: float,
) -> Sequence[Pnt]:
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
    theta_p = [theta_start + i * theta / (n_points - 1) for i in range(n_points)]
    return [endpoint(center, t, radius) for t in theta_p]


def endpoint(start: Pnt, angle: float, distance: float) -> Pnt:
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


def move_toward(start: Pnt, target: Pnt, distance: float) -> Pnt:
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


def rotate_and_move(start: Pnt, ref: Pnt, angle: float, distance: float):
    """Combine ``rotated_point`` and ``move_toward`` for convenience.

    Args:
        start: Starting point.
        ref: A reference point.
        angle: The angle in radians to rotate ``ref`` around start.
        distance: The distance to move from ``start``.

    Returns:
        A point ``distance`` from ``start`` in the ``angle`` direction
        relative to ``ref``.

    """
    x = rotated_point(ref, start, angle)
    return move_toward(start, x, distance)


def distance(p1: Pnt, p2: Pnt) -> float:
    """Get the distance between two points."""
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    return math.sqrt(dx * dx + dy * dy)


def direction_to(p1: Pnt, p2: Pnt) -> float:
    """Get the direction of p2 from p1 in degrees."""
    return deg(math.atan2(p2[1] - p1[1], p2[0] - p1[0]))


def get_nearest(
    points: Sequence[Pnt], point: Pnt, index: bool = False
) -> Union[Pnt, int]:
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


def midpoint(p1: Pnt, p2: Pnt) -> Pnt:
    """Get the midpoint between two points.

    Args:
        p1: A point.
        p2: Another point.

    """
    return (p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0


def angle_between(p1: Pnt, p2: Pnt, p3: Pnt) -> float:
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


def translated_point(point: Pnt, dx: float, dy: float) -> Pnt:
    """Get a translated point.

    Args:
        point: The starting location.
        dx: The horizontal translation.
        dy: The vertical translation.

    """
    return (point[0] + dx, point[1] + dy)


def rotated_point(point: Pnt, pivot: Pnt, angle: float) -> Pnt:
    """Get the new location of a point after rotating around a reference point.

    Args:
        point: The starting location.
        pivot: The center of rotation.
        angle: The angle in radians by which to rotate.

    """
    x = (
        ((point[0] - pivot[0]) * math.cos(angle))
        - ((point[1] - pivot[1]) * math.sin(angle))
        + pivot[0]
    )
    y = (
        ((point[1] - pivot[1]) * math.cos(angle))
        + ((point[0] - pivot[0]) * math.sin(angle))
        + pivot[1]
    )
    return (x, y)


def scaled_point(point: Pnt, cx: float, cy: float = None) -> Pnt:
    """Get the new location of ``point`` after scaling coordinates.

    Provide either one scaling factor or cx and cy.

    Args:
        cx: Either the scaling factor, or if ``cy`` is also provided,
          the horizontal scaling factor.
        cy: The vertical scaling factor.

    """
    cy = cx if cy is None else cy
    return (point[0] * cx, point[1] * cy)


def horizontal_range(points: Sequence[Pnt]) -> float:
    """Get the magnitude of the horizontal range of a list of points.

    Args:
        points: A list of points.

    """
    if len(points) == 0:
        return 0
    else:
        return max([x[0] for x in points]) - min([x[0] for x in points])


def translate_points(points: Sequence[Union[Pnt, Sequence]], dx: float, dy: float):
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


def rotate_points(
    points: Sequence[Union[Pnt, Sequence]], pivot: Pnt, angle: float
):
    """Rotate points around a reference point.

    Args:
        points: A list of points, which can be nested.
        pivot: The center of rotation.
        angle: The angle in radians by which to rotate.

    """
    for i in range(len(points)):
        if isinstance(points[i], list):
            rotate_points(points[i], pivot, angle)
        else:
            points[i] = rotated_point(points[i], pivot, angle)


def scale_points(
    points: Sequence[Union[Pnt, Sequence]], cx: float, cy: float = None
):
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


def jitter_points(points: Sequence[Pnt], r: float):
    """Add noise to the locations of points.

    Distance and direction of movement are both uniformly random, so
    the 2D probability density is circular with higher concentration
    toward the center.

    Args:
        points: A list of points.
        r: The maximum distance points will move.

    """
    angles = np.random.uniform(0, 2 * math.pi, size=len(points))
    dists = np.random.uniform(0, r, size=len(points))
    for i in range(len(points)):
        points[i] = endpoint(points[i], angles[i], dists[i])


def jittered_points(points: Sequence[Pnt], r: float) -> Sequence[Pnt]:
    """Get noisy copy of points.

    Like jitter_points but returns jittered points, not affecting the
    original list.

    Args:
        points: A list of points.
        r: The maximum distance points will move.

    Returns:
        A list of points.

    """
    x = points[:]
    jitter_points(x, r)
    return x


def line_to_polygon(points: Sequence[Pnt], width: float) -> Sequence[Pnt]:
    """Convert a sequence of points to a thin outline.

    Imagining the points were connected with a stroke with positive
    width, the outline of the stroke is returned.

    Args:
        points: A list of line points.
        width: Width of the stroke to be outlined.

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


def is_clockwise(points: Sequence[Pnt]) -> bool:
    """Determine the derection of a sequence of points around a polygon.

    Finds whether a set of polygon points goes in a clockwise or
    counterclockwise direction.  If edges cross, it gives the more
    prominent direction.

    Args:
        points: A list of polygon vertices.

    """
    p = points + [points[0]]
    edge_vals = [
        (p[i + 1][0] - p[i][0]) * (p[i + 1][1] + p[i][1]) for i in range(len(points))
    ]
    return sum(edge_vals) > 0
