"""
filaments.py
============
Create meandering segmented filaments.

"""

import math
import random

from .main import set_style, random_walk
from .geom import distance, endpoint, rad, midpoint, move_toward


def _next_segment(p1, p2, l1, l2):
    """Get next filament segment.

    Each segment is a trapezoid connected to adjacent segments along the
    same-length sides. Thus, the difference in lengths of the remaining two
    sides determines the angles, and consequently the filament curvature.

    Args:
        p1 (point): If segment is drawn above previous one, this is the lower left vertex of new segment.
        p2 (point): The lower right vertex of new segment.
        l1 (float|int): Length of side extending from p1.
        l2 (float|int): Length of side extending from p2.

    Returns:
        list: A list of four points starting with p1 and going around
        counter-clockwise.

    """
    s1_angle = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
    w = distance(p1, p2)
    a = (l2 - l1) / 2.
    theta_1 = math.acos(a / w)

    p3 = endpoint(p2, theta_1 + s1_angle, l1)
    p4 = endpoint(p1, theta_1 + s1_angle, l2)

    return [p1, p2, p3, p4]


def filament(start, direction, width, l_min, l_max, segments, l_max_step=None):
    """Generate a meandering segmented filament.

    Args:
        start (point): The midpoint of first edge of the filament.
        direction (number): The starting direction (in degrees) of the filament.
        width (float|int): The width of the filament (at segment joining edges).
        l_min (float|int): Minimum side length of segment.
        l_max (float|int): Maximum side length of segment.
        segments (int): Number of segments in filament.
        l_max_step (float|int): If not None, the edge lengths on each side of the filament will be determined by random walk, and this will be the maximum step size.

    Returns:
        list: A list of polygons (the segments in order).

    """
    p1 = endpoint(start, rad(direction + 90), width / 2.)
    p2 = endpoint(start, rad(direction - 90), width / 2.)

    if l_max_step is None:
        l1 = [random.uniform(l_min, l_max) for x in range(segments)]
        l2 = [random.uniform(l_min, l_max) for x in range(segments)]
    else:
        l1 = random_walk(min_val=l_min, max_val=l_max,
                         max_step=l_max_step, n=segments)
        l2 = random_walk(min_val=l_min, max_val=l_max,
                         max_step=l_max_step, n=segments)

    x = [_next_segment(p1, p2, l1[0], l2[0])]
    for i in range(1, segments):
        x.append(_next_segment(x[-1][3], x[-1][2], l1[i], l2[i]))

    polygons = [dict(type='polygon', points=p) for p in x]
    set_style(polygons, 'stroke', 'match')
    set_style(polygons, 'stroke_width', 0.3)
    return polygons


def _next_tapered_segment(p1, p2, l1, l2, shrinkage):
    """Get next tapered filament segment.

    Like tapered_segment, but the edge opposite p1-p2 shrinks for
    every segment.  When the starting edge reaches 1.5 times the
    shrinkage amount, a triangular segment is returned.

    Args:
        p1 (point): If segment is drawn above previous one, this is the lower left vertex of new segment.
        p2 (point): The lower right vertex of new segment.
        l1 (float|int): The length of the side extending from p1.
        l2 (float|int): The length of the side extending fom p2.
        shrinkage (float|int): Absolute decrease from starting to opposite edge.

    Returns:
        list: A list of four (or three) points starting with p1 and
        going around counter-clockwise.

    """
    s1_angle = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
    w = distance(p1, p2)
    a = (l2 - l1) / 2.
    theta_1 = math.acos(a / w)

    p3 = endpoint(p2, theta_1 + s1_angle, l1)
    p4 = endpoint(p1, theta_1 + s1_angle, l2)

    # 1.5 is arbitrary, but avoids near-zero width for last segment:
    if w <= 1.5 * shrinkage:
        return [p1, p2, midpoint(p3, p4)]
    else:
        p3 = move_toward(p3, p4, shrinkage / 2.)
        p4 = move_toward(p4, p3, shrinkage / 2.)
        return [p1, p2, p3, p4]


def tapered_filament(start, direction, width, l_min, l_max, segments,
                     l_max_step=None):
    """Generate a meandering segmented filament that tapers to a point.

    Args:
        start (point): The midpoint of first edge of the filament.
        direction (float|int): The starting direction (in degrees) of filament.
        width (float|int): The width of filament (at segment joining edges).
        l_min (float|int): Minimum side length of segment.
        l_max (float|int): Maximum side length of segment.
        segments (int): Number of segments in filament.
        l_max_step (float|int): If not None, the edge lengths on each side of the filament will be determined by random walk, and this will be the maximum step size.

    Returns:
        list: The ordered segment polygons.

    """
    if l_max_step is None:
        l_max_step = l_max - l_min
    shrinkage = float(width) / segments

    p1 = endpoint(start, rad(direction + 90), width / 2.)
    p2 = endpoint(start, rad(direction - 90), width / 2.)

    l1 = random.uniform(l_min, l_max)
    l2 = random.uniform(l_min, l_max)
    prev_l1 = l1
    prev_l2 = l2
    x = [_next_tapered_segment(p1, p2, l1, l2, shrinkage)]
    while len(x[-1]) == 4:
        scaling = distance(x[-1][3], x[-1][2]) / width
        # current_l_min = (l_min + l_max) / 2 - 0.5 * scaling * (l_max - l_min)
        # current_l_max = (l_min + l_max) / 2 + 0.5 * scaling * (l_max - l_min)
        current_l_min = l_min * scaling
        current_l_max = l_max * scaling
        current_step = l_max_step * scaling

        if l_max_step is None:
            l1 = random.uniform(current_l_min, current_l_max)
            l2 = random.uniform(current_l_min, current_l_max)
        else:
            l1 = random_walk(current_l_min, current_l_max,
                             current_step, n=2, start=prev_l1)[1]
            l2 = random_walk(current_l_min, current_l_max,
                             current_step, n=2, start=prev_l2)[1]
            prev_l1 = l1
            prev_l2 = l2

        x.append(_next_tapered_segment(x[-1][3], x[-1][2], l1, l2, shrinkage))

    polygons = [dict(type='polygon', points=p) for p in x]
    set_style(polygons, 'stroke', 'match')
    set_style(polygons, 'stroke_width', 0.3)
    return polygons
