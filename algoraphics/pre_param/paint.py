"""
paint.py
========
Create blow-paint effects along shape boundaries.

"""

import math
import numpy as np

from .geom import interpolate, move_toward, rotate_and_move, jittered_points
from .geom import is_clockwise, line_to_polygon, endpoint, rad


def _blow_paint_edge(start, end, spacing=20, length=40, len_dev=0.25, width=5):
    """Draw blow-paint shapes along an edge.

    Creates 'fingers' of paint along the edge, as if being blown along
    the page perpindicular to the edge.  Draws toward the right when
    facing start to end).

    Args:
        start (tuple): The starting point.
        end (tuple): The ending point.
        spacing (float): Average distance between paint fingers.
        length (float): Average length of the paint fingers.
        len_dev (float): The standard deviation of finger lengths relative to `length` (so it should be less than 1).
        width (float): Average thickness of each finger.

    """
    locs = [start, end]
    interpolate(locs, spacing)
    for i in range(1, len(locs) - 1):  # De-uniform spacing.
        r = np.random.uniform(-spacing / 4., spacing / 4.)
        locs[i] = move_toward(locs[i], start, r)
    pts = [start]
    for loc in locs[1:-1]:
        le = max(5, np.random.normal(length, length * len_dev))

        p1 = move_toward(loc, start, width / 2.)
        p2 = rotate_and_move(p1, loc, -math.pi / 2, le)
        pts_out = [p1, p2]
        interpolate(pts_out, min(20, le / 3.))
        # spread base and bulb:
        pts_out[0] = move_toward(pts_out[0], start, width / 2.)
        pts_out[-1] = rotate_and_move(pts_out[-1], pts_out[0], math.pi / 2,
                                      width / 6.)
        pts_out[1:-1] = jittered_points(pts_out[1:-1], width / 3., 'uniform')

        p3 = move_toward(loc, end, width / 2.)
        p4 = rotate_and_move(p3, loc, math.pi / 2, le)
        pts_in = [p4, p3]
        interpolate(pts_in, min(20, le / 3.))
        pts_in[-1] = move_toward(pts_in[-1], end, width / 2.)
        pts_in[0] = rotate_and_move(pts_in[0], pts_in[-1], -math.pi / 2,
                                    width / 6.)
        pts_in[1:-1] = jittered_points(pts_in[1:-1], width / 3., 'uniform')

        pts.extend(pts_out)
        pts.extend(pts_in)
        # Better without end point, since it is redundant with start
        # point of the next edge in the shape:
        # pts.append(end)
    return pts


def blow_paint_area(points, spacing=20, length=40, len_dev=0.25, width=5):
    """Draw a blow-paint effect around an area.

    Creates 'fingers' of paint projecting from each edge, as if being
    blown along the page perpindicular to the edge.

    Args:
        points (list): The vertices of the polygonal area.
        spacing (float): Average distance between paint fingers.
        length (float): Average length of the paint fingers.
        len_dev (float): The standard deviation of finger lengths relative to `length` (so it should be less than 1).
        width (float): Average thickness of each finger.

    """
    if is_clockwise(points):
        points = list(reversed(points))
    points.append(points[0])
    pts = []
    for i in range(len(points) - 1):
        pts.extend(_blow_paint_edge(points[i], points[i + 1], spacing,
                                    length, len_dev, width))
    return dict(type='spline', points=pts, circular=True, curvature=0.4)


def blow_paint_line(points, line_width=10, spacing=20, length=20,
                    len_dev=0.33, width=5):
    """Draw a blow-paint effect connecting a sequence of points.

    Creates 'fingers' of paint projecting from each edge, as if being
    blown along the page perpindicular to the edge (in both
    directions).

    Args:
        points (list): The points to connect.
        line_width (float): The thickness of the line (excluding the fingers).
        spacing (float): Average distance between paint fingers.
        length (float): Average length of the paint fingers.
        len_dev (float): The standard deviation of finger lengths relative to `length` (so it should be less than 1).
        width (float): Average thickness of each finger.

    """
    pts = line_to_polygon(points, line_width)
    return blow_paint_area(pts, spacing, length, len_dev, width)


def blow_paint_spot(point, length=10, len_dev=0.7, width=3):
    """Draw a paint splatter.

    Creates 'fingers' of paint projecting from a point.

    Args:
        point (tuple): The center of the splatter.
        length (float): Average length of the paint fingers.
        len_dev (float): The standard deviation of finger lengths relative to `length` (so it should be less than 1).
        width (float): Average thickness of each finger.

    """
    le = 10                     # Length of hexagon edge.
    offset = np.random.uniform(0, 60)
    pts = [endpoint(point, rad(i * 60 + offset), le) for i in range(6)]
    return blow_paint_area(pts, le - 1, length, len_dev, width)
