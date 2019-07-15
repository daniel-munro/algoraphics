"""
ripples.py
==========
Create space-filling ripple effects.

"""

import numpy as np
from typing import Union, Tuple, Dict, List, Sequence

from ..main import _markov_next, add_margin
from ..geom import rotated_point, rad, endpoint, distance, Rtree
from ..param import fixed_value
from ..shapes import spline

Number = Union[int, float]
Point = Tuple[Number, Number]


def _next_point(points: Rtree, spacing: Number,
                mode: str) -> Union[Point, None]:
    """Continue from last two elements of ``points``."""
    last = points.points[-2:]
    if mode == 'R':
        angle = 60
        angle_inc = 5
        stop_angle = 300
        newpt_fun = lambda ang: rotated_point(last[-2], last[-1], rad(ang))
    elif mode == 'L':
        angle = 300
        angle_inc = -5
        stop_angle = 60
        newpt_fun = lambda ang: rotated_point(last[-2], last[-1], rad(ang))
    elif mode == 'S':
        angle = np.random.choice(range(360))
        direction = np.random.choice([-1, 1])
        angle_inc = direction * 1
        stop_angle = angle + direction * 359
        newpt_fun = lambda ang: endpoint(last[-1], angle, spacing)
    elif mode == 'X':
        angle = np.random.choice(range(120, 241))
        direction = np.random.choice([-1, 1])
        angle_inc = direction * 1
        stop_angle = angle + direction * 359
        newpt_fun = lambda ang: rotated_point(last[-2], last[-1], rad(ang))

    while True:
        newpt = newpt_fun(angle)
        # 0.999 to allow for last point
        if distance(newpt, points.nearest(newpt)) >= spacing * 0.999:
            return newpt
        elif angle == stop_angle:
            return None
        else:
            angle += angle_inc


def _scan_for_space(open_space: Sequence[Point], points:
                    Sequence[Point], spacing: Number) -> Union[Point, None]:
    """Look for new starting point.

    Since a new ripple needs to be drawn with spacing on either side,
    there must be fewer than 6 existing points within 2 * ``spacing``
    of the new starting point.

    Args:
        open_space: List of randomly ordered coordinates that have not
          yet been looked at.
        points: Existing ripple points.
        spacing: Distance between ripples.

    Returns:
        Either an available starting point or None if there is none available.

    """
    while len(open_space) > 0:
        newpt = open_space.pop()
        neighbors = points.nearest(newpt, 6)
        # <= 5 in vicinity still has space somewhere to go
        if distance(newpt, neighbors[-1]) >= spacing * 2:
            if distance(newpt, neighbors[0]) >= spacing:
                return newpt
    return None


def ripple_canvas(w: Number, h: Number, spacing: Number,
                  trans_probs: Dict[str, Dict[str, float]] = None,
                  existing_pts: Sequence[Point] = None) -> List[dict]:
    """Fill the canvas with ripples.

    The behavior of the ripples is determined by a first-order Markov
    chain in which events correspond to points along splines.  The
    states are 'S', 'R', 'L', and 'X'.  At 'S', the ripple begins in a
    random direction.  At 'R', the ripple turns right sharply until
    encountering a ripple or other barrier, and then follows along it.
    Likewise with 'L' turning left.  At 'X', the ripple moves straight
    forward +/- up to 60 degrees.  Higher state-changing transition
    probabilities result in more erratic ripples.

    Args:
        w: Width of the canvas.
        h: Height of the canvas.
        spacing: Distance between ripples.
        trans_probs: A dictionary of dictionaries containing Markov
          chain transition probabilities from one state (first key) to
          another (second key).
        existing_pts: An optional list of points that ripples will avoid.

    Returns:
        The ripple splines.

    """
    w = fixed_value(w)
    h = fixed_value(h)
    spacing = fixed_value(spacing)
    if trans_probs is None:
        trans_probs = dict(S=dict(R=1), R=dict(R=1))

    margin = 3
    bounds = add_margin((0, 0, w, h), margin)

    curves = []  # list of list of points that will become paths
    allpts = Rtree(existing_pts)  # for finding neighbors

    pts = [(x, bounds[1]) for x in np.arange(bounds[0], bounds[2], spacing)]
    pts.extend([(bounds[2], y) for y in
                np.arange(bounds[1], bounds[3], spacing)])
    pts.extend([(x, bounds[3]) for x in
                np.arange(bounds[2], bounds[0], -spacing)])
    pts.extend([(bounds[0], y) for y in
                np.arange(bounds[3], bounds[1], -spacing)])
    curves.append(pts)
    allpts.add_points(pts)

    precision = 5
    xvals = np.arange(bounds[0], bounds[2], precision)
    yvals = np.arange(bounds[1], bounds[3], precision)
    open_space = [(x, y) for x in xvals for y in yvals]
    np.random.shuffle(open_space)

    start = _scan_for_space(open_space, allpts, spacing)
    pts = [start]
    allpts.add_point(start)

    mode = 'S'
    more_space = True
    while more_space:
        newpt = _next_point(allpts, spacing, mode)
        if newpt is not None:
            pts.append(newpt)
            allpts.add_point(newpt)
            mode = _markov_next(mode, trans_probs)
        else:
            curves.append(pts)
            new_start = _scan_for_space(open_space, allpts, spacing)
            if new_start is not None:
                pts = [new_start]
                allpts.add_point(new_start)
                mode = 'S'
            else:
                more_space = False

    paths = [spline(points=p, fill='none', stroke='black') for p in curves]
    return paths
