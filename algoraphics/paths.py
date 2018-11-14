"""
paths.py
========
Generate path strings.

"""

import math

from .geom import rotated_point, angle_between, move_toward, distance, endpoint
from .geom import rad
from .param import fixed_value, make_param


def _polygon_path(points):
    """Generate path string for a polygon.

    Args:
        points (list): A list of points.

    Returns:
        str: An SVG path.

    """
    output = 'M' + str(points[0][0]) + ' ' + str(points[0][1]) + ' '
    for point in points[1:]:
        output += 'L' + str(point[0]) + ' ' + str(point[1]) + ' '
    output += 'Z'
    return output


def _spline_path(points, curvature=0.3, circular=False):
    """Generate path string for spline.

    Args:
        points (list): A list of points.
        curvature (number): The distance to the control point relative to the distance to the adjacent point. Usually between zero and one.
        circular (bool): If False, spline ends reasonably at the first and last points.  If True, the ends of the spline will connect smoothly.

    Returns:
        str: An SVG path.

    """
    if circular:
        points = [points[-1]] + points + [points[0], points[1]]
    else:
        p0 = rotated_point(points[1], points[0], math.pi)
        p_last = rotated_point(points[-2], points[-1], math.pi)
        # Add reasonable control points at ends:
        points = [p0] + points + [p_last]

    path = "M " + str(points[1][0]) + " " + str(points[1][1]) + " "
    for i in range(2, len(points) - 1):
        theta1 = angle_between(points[i], points[i - 1], points[i - 2])
        b1 = rotated_point(points[i],
                           points[i - 1],
                           ((theta1 / 2) % math.pi) - math.pi / 2)
        # c1 = midpoint(points[i - 1], b1)
        c1 = move_toward(points[i - 1], b1,
                         curvature * distance(points[i - 1], b1))

        theta2 = angle_between(points[i - 1], points[i], points[i + 1])
        b2 = rotated_point(points[i - 1],
                           points[i],
                           ((theta2 / 2) % math.pi) - math.pi / 2)
        # c2 = midpoint(points[i], b2)
        c2 = move_toward(points[i], b2, curvature * distance(points[i], b2))

        path += "C " + str(c1[0]) + " " + str(c1[1]) + " "
        path += str(c2[0]) + " " + str(c2[1]) + " "
        path += str(points[i][0]) + " " + str(points[i][1]) + " "
    return path


def _write_path(d):
    """TODO"""
    def pnt(p):
        return str(p[0]) + ' ' + str(p[1])

    def write_path_comp(comp):
        if comp['command'] == 'M' or comp['command'] == 'L':
            s = comp['command'] + ' ' + pnt(comp['to'])
        elif comp['command'] == 'C':
            s = ' '.join(['C', pnt(comp['c1']), pnt(comp['c2']),
                          pnt(comp['to'])])
        elif comp['command'] == 'A':
            if 'large_arc' not in comp:
                comp['large_arc'] = False
            # for now I'm using a single r instead of rx and ry:
            s = ' '.join(['A', str(comp['r']), str(comp['r']), '0'])
            s += ' 1' if comp['large_arc'] else ' 0'
            # Normally positive is 0 but is switched because I flip
            # the whole canvas.
            s += ' 1' if comp['positive'] else ' 0'
            s += ' ' + pnt(comp['to'])
        elif comp['command'] == 'Z':
            s = 'Z'
        return s
    return ' '.join([write_path_comp(comp) for comp in d])


def polygon(points):
    return dict(type='polygon', points=points)


def spline(points):
    return dict(type='spline', points=points)


def wave(start, direction, width, period, length):
    """Generate a wave spline.

    Args:
        start (point): Starting point of the wave.
        direction (float|int): Direction (in degrees) of the wave.
        width (float|int): The total amplitude of the wave from peak to trough.
        period (float|int): Period of the wave.
        length (float|int): End-to-end length of the wave.

    Returns:
        dict: A spline shape.

    """
    start = fixed_value(start)
    direction = fixed_value(direction)
    width = fixed_value(width)
    period = make_param(period)

    points = [endpoint(start, rad(direction + 90), width / 2.)]
    phase = 0
    ref_point = start
    while distance(start, points[-1]) < length:
        phase = (phase + 1) % 2
        ref_point = endpoint(ref_point, rad(direction), period.value() / 2.)
        if phase == 0:
            points.append(endpoint(ref_point, rad(direction + 90), width / 2.))
        else:
            points.append(endpoint(ref_point, rad(direction - 90), width / 2.))
    return spline(points=points)


def rectangle(start=None, w=None, h=None, bounds=None):
    """TODO"""
    start = (fixed_value(start[0]), fixed_value(start[1]))
    w = fixed_value(w)
    h = fixed_value(h)
    if bounds is not None:
        bounds = tuple([fixed_value(b) for b in bounds])

    if start is not None:
        assert w is not None and h is not None
        pts = [start,
               (start[0] + w, start[1]),
               (start[0] + w, start[1] + h),
               (start[0], start[1] + h)]
    else:
        pts = [(bounds[0], bounds[2]), (bounds[1], bounds[2]),
               (bounds[1], bounds[3]), (bounds[0], bounds[3])]
    return dict(type='polygon', points=pts)


def circle(c, r):
    """TODO"""
    c = fixed_value(c)
    r = fixed_value(r)
    return dict(type='circle', c=c, r=r)
