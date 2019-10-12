"""
utils.py
========
Functions used in the extras library.

"""

import numpy as np
import rtree
from typing import Dict, List, Union, Tuple, Sequence

from ..color import Color, make_color
from ..geom import distance, jitter_points, endpoint, rad
from ..shapes import Shape, Group, Polygon, Spline, Line, Circle

Pnt = Tuple[float, float]
Bounds = Tuple[float, float, float, float]
Collection = Union[list, Shape, Group]


def _markov_next(state: str, trans_probs: Dict[str, Dict[str, float]]) -> str:
    """Get the next state in a first-order Markov chain.

    Args:
        state: The current state.
        trans_probs: A dictionary of dictionaries containing
          transition probabilities from one state (first key) to
          another (second key).

    Returns:
        The next state.

    """
    states = list(trans_probs[state].keys())
    probs = [trans_probs[state][s] for s in states]
    return np.random.choice(states, p=probs)


def contrasting_lightness(color: Color, light_diff: float) -> Color:
    """Get color with contrasting lightness to reference color.

    Color is lighter if original lightness is < 0.5 and darker otherwise.
    Used to create color pairs for a mixture of light and dark colors.

    Args:
        color: A color.
        light_diff: Magnitude of difference in lightness, between 0 and 1.

    Returns:
        The contrasting color.

    """
    col = make_color(color)
    hsl = (col.hue.state(), col.sat.state(), col.li.state())
    if hsl[2] < 0.5:
        new_light = min(hsl[2] + light_diff, 1.0)
    else:
        new_light = max(hsl[2] - light_diff, 0.0)
    new_hsl = (hsl[0], hsl[1], new_light)
    return Color(*new_hsl)


class Rtree:
    """An object to efficiently query a field of points.

    Args:
        points: Starting points.

    """

    def __init__(self, points: Sequence[Pnt] = None):
        if points is None:
            points = []
        self.idx = rtree.index.Index()
        self.points = []  # for retrieving points, e.g. last N
        self.size = 0
        for p in points:
            self.add_point(p)

    def add_point(self, point: Pnt):
        """Add a point to the collection.

        Args:
            point: The new point.

        """
        self.idx.add(self.size, point)
        self.points.append(point)
        self.size += 1

    def add_points(self, points: Sequence[Pnt]):
        """Add points to the collection.

        Args:
            points: The new points.

        """
        for point in points:
            self.add_point(point)

    def nearest(
        self, point: Pnt, n: int = 1, index: bool = False
    ) -> Union[Sequence[Pnt], Pnt]:
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


def spaced_points(n: int, bounds: Bounds, n_cand: int = 10) -> List[Pnt]:
    """Generate random but evenly-spaced points.

    Uses Mitchell's best-candidate algorithm.

    Args:
        n: Number of points to generate.
        bounds: A bounds tuple.
        n_cand: Number of candidate points to generate for each output
          point.  Higher numbers result in higher regularity.

    Returns:
        The generated points.

    """
    x_min, y_min, x_max, y_max = bounds
    points = [(np.random.uniform(x_min, x_max), np.random.uniform(y_min, y_max))]
    idx = Rtree(points)

    for i in range(1, n):
        best_distance = 0
        for j in range(n_cand):
            cand = (np.random.uniform(x_min, x_max), np.random.uniform(y_min, y_max))
            nearest = idx.nearest(cand)
            dist = distance(nearest, cand)
            if dist > best_distance:
                best_distance = dist
                best_candidate = cand
        points.append(best_candidate)
        idx.add_point(best_candidate)
    return points


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


def wobble(shapes: Sequence, dev: float = 2):
    """Add a little messiness to perfect lines and curves.

    Convert straight lines and curves into slightly wavy splines.
    Currently it converts the shape into a shape with fixed
    parameters, since it has to do point interpolation.  The new
    shape's parameters can later be made dynamic.

    Args:
        obj: A list of one or more shapes (can be nested).
        dev: The (approximate) maximum distance a part of an edge will
          move.

    """
    for i, obj in enumerate(shapes):
        if type(obj) is list:
            wobble(obj, dev)
        elif type(obj) is Group:
            wobble(obj.clip, dev)
            wobble(obj.members, dev)
        elif type(obj) is Line:
            shapes[i] = _wobble_polyline(obj, dev)
        elif type(obj) is Polygon:
            shapes[i] = _wobble_polygon(obj, dev)
        elif type(obj) is Spline:
            if obj.circular:
                shapes[i] = _wobble_polygon(obj, dev)
            else:
                shapes[i] = _wobble_polyline(obj, dev)
        elif type(obj) is Circle:
            shapes[i] = _wobble_circle(obj, dev)


def _wobble_polyline(obj: dict, dev: float):
    pts = [pt.state() for pt in obj.points]
    remove_close_points(pts, 2 * dev)
    interpolate(pts, 10)
    jitter_points(pts, dev)
    return Spline(pts, **obj.style)


def _wobble_polygon(obj: dict, dev: float):
    pts = [pt.state() for pt in obj.points]
    pts.append(pts[0])
    remove_close_points(pts, 2 * dev)
    interpolate(pts, 10)
    del pts[-1]
    jitter_points(pts, dev)
    return Spline(pts, circular=True, **obj.style)


def _wobble_circle(obj: dict, dev: float):
    r, c = obj.r.state(), obj.c.state()
    n_pts = round(2 * r * np.pi / 10)
    direcs = np.arange(n_pts) / n_pts * 2 * np.pi
    pts = [endpoint(c, direc, r) for direc in direcs]
    jitter_points(pts, dev)
    return Spline(pts, circular=True, **obj.style)
