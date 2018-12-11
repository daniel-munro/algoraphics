"""
forms.py
============
Create forms such as filaments and trees.

"""

import math
import numpy as np
from typing import Union, Tuple, Sequence, List

from .main import set_style
from .param import fixed_value, make_param
from .geom import endpoint, rad, is_clockwise, interpolate, move_toward
from .geom import rotate_and_move, jittered_points, line_to_polygon
from .shapes import polygon, spline, line
from .param import Param

Number = Union[int, float]
Point = Tuple[Number, Number]


def filament(start: Point, direction: Param, width: Param, seg_length:
             Param, n_segments: int) -> List[dict]:
    """Generate a meandering segmented filament.

    Args:
        start: The midpoint of first edge of the filament.
        direction: The direction (in degrees) of each segment.
          Recommended to be a Param with a delta Param for a
          meandering filament.  Nested delta Params will produce
          meandering from higher-order random walks.
        width: The width of the filament (at segment joining edges).
        seg_length: Average side length of each segment.
        n_segments: Number of segments in the filament.

    Returns:
        A list of polygons (the segments from start to end).

    """
    start = fixed_value(start)
    direction = make_param(direction)
    width = make_param(width)
    seg_length = make_param(seg_length)
    n_segments = fixed_value(n_segments)

    dirs = [direction.value() for i in range(n_segments)]
    widths = [width.value() for i in range(n_segments)]
    lengths = [seg_length.value() for i in range(n_segments)]

    backbone = [start]
    for i in range(n_segments):
        pt = endpoint(backbone[-1], rad(dirs[i]), lengths[i])
        backbone.append(pt)

    # Filament starts with right angles:
    p1 = endpoint(start, rad(dirs[0] + 90), widths[0] / 2)
    p2 = endpoint(start, rad(dirs[0] - 90), widths[0] / 2)
    pt_pairs = [[p1, p2]]
    for i in range(1, n_segments):
        angle = dirs[i] - dirs[i-1]
        angle = (180 + (dirs[i-1] - dirs[i])) / 2
        # Points are more than width / 2 from backbone to account for
        # the angles, so the trapezoids are the correct width.
        dist = widths[i] / (2 * math.sin(rad(angle)))
        p1 = endpoint(backbone[i], rad(dirs[i] + angle), dist)
        p2 = endpoint(backbone[i], rad(dirs[i] + angle + 180), dist)
        pt_pairs.append([p1, p2])
    # Filament ends with right angles:
    p1 = endpoint(backbone[-1], rad(dirs[-1] + 90), widths[-1] / 2)
    p2 = endpoint(backbone[-1], rad(dirs[-1] - 90), widths[-1] / 2)
    pt_pairs.append([p1, p2])

    segments = []
    for i in range(n_segments):
        pts = [pt_pairs[i][0], pt_pairs[i][1],
               pt_pairs[i+1][1], pt_pairs[i+1][0]]
        segments.append(polygon(points=pts))

    set_style(segments, 'stroke', 'match')
    set_style(segments, 'stroke-width', 0.3)

    # For debugging:
    # x = [dict(type='circle', c=p, r=2) for p in backbone]
    # return [segments, x]

    return segments


def tentacle(start: Point, direction: Param, length: Number, width:
             Param, seg_length: Number) -> List[dict]:
    """Generate a filament that tapers to a point.

    Args:
        start: The midpoint of first edge of the tentacle.
        direction: The direction (in degrees) of each segment.
          Recommended to be a Param with a delta Param for a
          meandering filament.  Nested delta Params will produce
          meandering from higher-order random walks.
        length: Approximate length of the tentacle.
        width: The starting width of the tentacle.
        seg_length: Average starting length of each segment.  They
          will shrink toward to the tip.

    Returns:
        A list of polygons (the segments from base to tip).

    """
    width = fixed_value(width)
    seg_length = fixed_value(seg_length)
    length = fixed_value(length)

    # Seg lengths will shrink from seg_length to 1/2 seg_length:
    n_segments = int(length / (0.75 * seg_length))
    width = Param(width, delta=-(width / n_segments))
    seg_length = Param(seg_length, delta=-(seg_length / (2 * n_segments)))
    return filament(start, direction, width, seg_length, n_segments)


def _blow_paint_edge(start: Point, end: Point, spacing: Number = 20,
                     length: Number = 40, len_dev: float = 0.25,
                     width: Number = 5) -> List[Point]:
    """Draw blow-paint shapes along an edge.

    Creates 'fingers' of paint along the edge, as if being blown along
    the page perpindicular to the edge.  Draws toward the right when
    facing start to end).

    Args:
        start: The starting point.
        end: The ending point.
        spacing: Average distance between paint fingers.
        length: Average length of the paint fingers.
        len_dev: The standard deviation of finger lengths relative to
          ``length`` (so it should be less than 1).
        width: Average thickness of each finger.

    Returns:
        A list of points to be connected in a spline.

    """
    locs = [start, end]
    interpolate(locs, spacing)
    for i in range(1, len(locs) - 1):  # De-uniform spacing.
        r = np.random.uniform(-spacing / 4, spacing / 4)
        locs[i] = move_toward(locs[i], start, r)
    pts = [start]
    for loc in locs[1:-1]:
        le = max(5, np.random.normal(length, length * len_dev))

        p1 = move_toward(loc, start, width / 2)
        p2 = rotate_and_move(p1, loc, -math.pi / 2, le)
        pts_out = [p1, p2]
        interpolate(pts_out, min(20, le / 3))
        # spread base and bulb:
        pts_out[0] = move_toward(pts_out[0], start, width / 2)
        pts_out[-1] = rotate_and_move(pts_out[-1], pts_out[0], math.pi / 2,
                                      width / 6)
        pts_out[1:-1] = jittered_points(pts_out[1:-1], width / 3, 'uniform')

        p3 = move_toward(loc, end, width / 2)
        p4 = rotate_and_move(p3, loc, math.pi / 2, le)
        pts_in = [p4, p3]
        interpolate(pts_in, min(20, le / 3))
        pts_in[-1] = move_toward(pts_in[-1], end, width / 2)
        pts_in[0] = rotate_and_move(pts_in[0], pts_in[-1], -math.pi / 2,
                                    width / 6)
        pts_in[1:-1] = jittered_points(pts_in[1:-1], width / 3, 'uniform')

        pts.extend(pts_out)
        pts.extend(pts_in)
        # Better without end point, since it is redundant with start
        # point of the next edge in the shape:
        # pts.append(end)
    return pts


def blow_paint_area(points: Sequence[Point], spacing: Number = 20,
                    length: Number = 40, len_dev: float = 0.25,
                    width: Number = 5) -> dict:
    """Draw a blow-paint effect around an area.

    Creates 'fingers' of paint projecting from each edge, as if being
    blown along the page perpindicular to the edge.

    Args:
        points: The vertices of the polygonal area.
        spacing: Average distance between paint fingers.
        length: Average length of the paint fingers.
        len_dev: The standard deviation of finger lengths relative to
          ``length`` (so it should be less than 1).
        width: Average thickness of each finger.

    """
    if is_clockwise(points):
        points = list(reversed(points))
    points.append(points[0])
    pts = []
    for i in range(len(points) - 1):
        pts.extend(_blow_paint_edge(points[i], points[i + 1], spacing,
                                    length, len_dev, width))
    return spline(points=pts, circular=True, curvature=0.4)


def blow_paint_line(points: Sequence[Point], line_width: Number = 10,
                    spacing: Number = 20, length: Number = 20,
                    len_dev: float = 0.33, width: Number = 5) -> dict:
    """Draw a blow-paint effect connecting a sequence of points.

    Creates 'fingers' of paint projecting from each edge, as if being
    blown along the page perpindicular to the edge (in both
    directions).

    Args:
        points: The points to connect.
        line_width: The thickness of the line (excluding the fingers).
        spacing: Average distance between paint fingers.
        length: Average length of the paint fingers.
        len_dev: The standard deviation of finger lengths relative to
          ``length`` (so it should be less than 1).
        width: Average thickness of each finger.

    """
    pts = line_to_polygon(points, line_width)
    return blow_paint_area(pts, spacing, length, len_dev, width)


def blow_paint_spot(point: Point, length: Number = 10, len_dev: float
                    = 0.7, width: Number = 3) -> dict:
    """Draw a paint splatter.

    Creates 'fingers' of paint projecting from a point.

    Args:
        point: The center of the splatter.
        length: Average length of the paint fingers.
        len_dev: The standard deviation of finger lengths relative to
          ``length`` (so it should be less than 1).
        width: Average thickness of each finger.

    """
    le = 10                     # Length of hexagon edge.
    offset = np.random.uniform(0, 60)
    pts = [endpoint(point, rad(i * 60 + offset), le) for i in range(6)]
    return blow_paint_area(pts, le - 1, length, len_dev, width)


def tree(start: Point, direction: Number, branch_length: Param, theta:
         Param, p: Param) -> List[dict]:
    """Generate a tree with randomly terminating branches.

    Args:
        start: The starting point.
        direction: The starting direction (in degrees).
        branch_length: Branch length.
        theta: The angle (in degrees) between sibling branches.
        p: The probability that a given branch will split instead of
          terminating.  Recommended to have a delta < 0 or ratio < 1
          so that the tree is guaranteed to terminate.

    Returns:
        A list of line shapes.

    """
    start = fixed_value(start)
    direction = fixed_value(direction)
    branch_length = make_param(branch_length)
    theta = make_param(theta)
    p = make_param(p)

    length = branch_length.value()
    end = endpoint(start, rad(direction), length)
    x = [line(p1=start, p2=end)]
    if np.random.random() < p.value():
        theta_this = theta.value()
        x.extend(tree(end, direction + theta_this / 2, branch_length,
                      theta, p))
        x.extend(tree(end, direction - theta_this / 2, branch_length,
                      theta, p))
    return x
