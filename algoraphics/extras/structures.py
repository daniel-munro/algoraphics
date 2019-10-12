"""
structures.py
=============
Create structures such as filaments and trees.

"""

import numpy as np
import copy
from typing import Tuple, Sequence, List

from ..geom import (
    endpoint,
    rad,
    move_toward,
    rotate_and_move,
    line_to_polygon,
    jittered_points,
)
from ..shapes import Polygon, Spline, Line
from ..param import Param, fixed_value, make_param
from ..point import Point, Move, make_point
from .utils import is_clockwise, interpolate

# Number = Union[int, float]
# Point = Tuple[Number, Number]
Pnt = Tuple[float, float]


def filament(backbone: Sequence[Point], width: Param) -> List[Polygon]:
    """Generate a meandering segmented filament.

    Args:
        backbone: A list of Points specifying the midpoint of the
          filament ends and segment boundaries.
        width: The width/s of the filament (at segment joining edges).

    Returns:
        A list of Polygons (the segments from start to end).

    """
    width = make_param(width)
    widths = [copy.copy(width) for i in range(len(backbone) + 1)]
    # Filament starts with right angles:
    p1 = Move(backbone[0], direction=backbone[1].direction + 90, distance=widths[0] / 2)
    p2 = Move(backbone[0], direction=backbone[1].direction - 90, distance=widths[0] / 2)
    pt_pairs = [[p1, p2]]
    for i in range(1, len(backbone) - 1):
        angle = (180 + (backbone[i].direction - backbone[i + 1].direction)) / 2
        p1 = Move(
            backbone[i],
            direction=(backbone[i + 1].direction + angle),
            distance=widths[i] / 2,
        )
        p2 = Move(
            backbone[i],
            direction=(backbone[i + 1].direction + angle + 180),
            distance=widths[i] / 2,
        )
        pt_pairs.append([p1, p2])
    # Filament ends with right angles:
    p1 = Move(
        backbone[-1], direction=backbone[-1].direction + 90, distance=widths[-1] / 2
    )
    p2 = Move(
        backbone[-1], direction=backbone[-1].direction - 90, distance=widths[-1] / 2
    )
    pt_pairs.append([p1, p2])

    segments = []
    for i in range(len(backbone) - 1):
        pts = [pt_pairs[i][0], pt_pairs[i][1], pt_pairs[i + 1][1], pt_pairs[i + 1][0]]
        segments.append(Polygon(pts))

    # set_style(segments, "stroke", "match")
    # set_style(segments, "stroke-width", 0.3)
    return segments


def tentacle(backbone: Sequence[Point], width: Param) -> Spline:
    """Generate a tentacle.

    Args:
        backbone: A list of Points specifying the midpoint of the
          filament ends and segment boundaries.
        width: The width of the tentacle base.

    Returns:
        A Spline shape.

    """
    # width = fixed_value(width)
    # x = filament(backbone, width)
    # delwidth = width / len(x)
    # for segment in x:
    #     width -= delwidth
    #     segment.points[2].distance = Param(width / 2)
    #     segment.points[3].distance = Param(width / 2)
    # return x
    width = make_param(width)
    delwidth = width / (len(backbone) - 1)
    # Tentacle starts with right angles:
    p1 = Move(backbone[0], direction=backbone[1].direction + 90, distance=width / 2)
    p2 = Move(backbone[0], direction=backbone[1].direction - 90, distance=width / 2)
    sides = [[p1], [p2]]  # Store points for each side.
    for i in range(1, len(backbone) - 1):
        width = width - delwidth
        angle = (180 + (backbone[i].direction - backbone[i + 1].direction)) / 2
        p1 = Move(
            backbone[i],
            direction=(backbone[i + 1].direction + angle),
            distance=width / 2,
        )
        p2 = Move(
            backbone[i],
            direction=(backbone[i + 1].direction + angle + 180),
            distance=width / 2,
        )
        sides[0].append(p1)
        sides[1].append(p2)
    points = sides[0] + list(reversed(sides[1]))
    tentacle = Spline(points, circular=True)
    return tentacle


def _blow_paint_edge(
    start: Pnt,
    end: Pnt,
    spacing: float = 20,
    length: float = 40,
    len_dev: float = 0.25,
    width: float = 5,
) -> List[Pnt]:
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
        p2 = rotate_and_move(p1, loc, -np.pi / 2, le)
        pts_out = [p1, p2]
        interpolate(pts_out, min(20, le / 3))
        # spread base and bulb:
        pts_out[0] = move_toward(pts_out[0], start, width / 2)
        pts_out[-1] = rotate_and_move(pts_out[-1], pts_out[0], np.pi / 2, width / 6)
        pts_out[1:-1] = jittered_points(pts_out[1:-1], width / 3)

        p3 = move_toward(loc, end, width / 2)
        p4 = rotate_and_move(p3, loc, np.pi / 2, le)
        pts_in = [p4, p3]
        interpolate(pts_in, min(20, le / 3))
        pts_in[-1] = move_toward(pts_in[-1], end, width / 2)
        pts_in[0] = rotate_and_move(pts_in[0], pts_in[-1], -np.pi / 2, width / 6)
        pts_in[1:-1] = jittered_points(pts_in[1:-1], width / 3)

        pts.extend(pts_out)
        pts.extend(pts_in)
        # Better without end point, since it is redundant with start
        # point of the next edge in the shape:
        # pts.append(end)
    return pts


def blow_paint_area(
    points: Sequence[Pnt],
    spacing: float = 20,
    length: float = 40,
    len_dev: float = 0.25,
    width: float = 5,
) -> dict:
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
        pts.extend(
            _blow_paint_edge(points[i], points[i + 1], spacing, length, len_dev, width)
        )
    return Spline(pts, circular=True, smoothing=0.4)


def blow_paint_line(
    points: Sequence[Pnt],
    line_width: float = 10,
    spacing: float = 20,
    length: float = 20,
    len_dev: float = 0.33,
    width: float = 5,
) -> dict:
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


def blow_paint_spot(
    point: Pnt, length: float = 10, len_dev: float = 0.7, width: float = 3
) -> dict:
    """Draw a paint splatter.

    Creates 'fingers' of paint projecting from a point.

    Args:
        point: The center of the splatter.
        length: Average length of the paint fingers.
        len_dev: The standard deviation of finger lengths relative to
          ``length`` (so it should be less than 1).
        width: Average thickness of each finger.

    """
    le = 10  # Length of hexagon edge.
    offset = np.random.uniform(0, 60)
    pts = [endpoint(point, rad(i * 60 + offset), le) for i in range(6)]
    return blow_paint_area(pts, le - 1, length, len_dev, width)


def tree(
    start: Point,
    direction: Param,
    branch_length: Param,
    theta: Param,
    p: float,
    delta_p: float = 0,
) -> List[dict]:
    """Generate a tree with randomly terminating branches.

    Args:
        start: The starting point.
        direction: The starting direction (in degrees).
        branch_length: Branch length.
        theta: The angle (in degrees) between sibling branches.
        p: The probability that a given branch will split instead of
          terminating.  Recommended to have a delta < 0 or ratio < 1
          so that the tree is guaranteed to terminate.
        delta_p: The decrease in p at each branching.

    Returns:
        A list of line shapes.

    """
    start = make_point(start)
    direction = make_param(direction)
    branch_length = copy.deepcopy(make_param(branch_length))
    theta = copy.deepcopy(make_param(theta))
    p = fixed_value(p)

    end = Move(start, direction, branch_length)
    x = [Line(p1=start, p2=end)]
    if np.random.random() < p:
        p += fixed_value(delta_p)
        x.extend(tree(end, direction + theta / 2, branch_length, theta, p, delta_p))
        x.extend(tree(end, direction - theta / 2, branch_length, theta, p, delta_p))
    return x
