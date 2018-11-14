"""
filaments.py
============
Create meandering segmented filaments.

"""

import math

from .main import set_style
from .param import fixed_value, make_param
from .geom import endpoint, rad


def filament(start, direction, width, seg_length, n_segments):
    """Generate a meandering segmented filament.

    Args:
        start (point): The midpoint of first edge of the filament.
        direction (Param): The direction (in degrees) of each segment.  Recommended to be a Param with a delta Param for a meandering filament.  Nested delta Params will produce meandering from higher-order random walks.
        width (float|int): The width of the filament (at segment joining edges).
        seg_length (float|int): Average side length of each segment.
        n_segments (int): Number of segments in the filament.

    Returns:
        list: A list of polygons (the segments in order).

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
        segments.append(dict(type='polygon', points=pts))

    set_style(segments, 'stroke', 'match')
    set_style(segments, 'stroke_width', 0.3)

    # For debugging:
    # x = [dict(type='circle', c=p, r=2) for p in backbone]
    # return [segments, x]

    return segments
