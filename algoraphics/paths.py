"""
paths.py
========
Generate path strings.

"""

import math

from .geom import translated_point, rotated_point, scaled_point, angle_between
from .geom import move_toward, distance, rad


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


def path_points(path):
    """Get skeleton points of path.

    Useful for finding an approximate bounding box for a path.

    """
    pts = []
    for cmd in path['d']:
        if 'to' in cmd:
            pts.append(cmd['to'])
    return pts


def translate_path(path, dx, dy):
    """TODO"""
    for comp in path:
        if comp['command'] in ['M', 'L', 'A']:
            comp['to'] = translated_point(comp['to'], dx, dy)
        elif comp['command'] == 'C':
            comp['c1'] = translated_point(comp['c1'], dx, dy)
            comp['c2'] = translated_point(comp['c2'], dx, dy)
            comp['to'] = translated_point(comp['to'], dx, dy)


def rotate_path(path, angle, pivot=(0, 0)):
    """TODO"""
    for comp in path:
        if comp['command'] in ['M', 'L']:
            comp['to'] = rotated_point(comp['to'], pivot, rad(angle))
        elif comp['command'] == 'C':
            comp['c1'] = rotated_point(comp['c1'], pivot, rad(angle))
            comp['c2'] = rotated_point(comp['c2'], pivot, rad(angle))
            comp['to'] = rotated_point(comp['to'], pivot, rad(angle))
        elif comp['command'] == 'A':
            # for now I'm using a single r instead of rx and ry
            # if comp['rx'] != comp['ry']:
                # comp['rotation'] = (comp['rotation'] + angle) % 360
            comp['to'] = rotated_point(comp['to'], pivot, rad(angle))


def scale_path(path, cx, cy=None):
    """Resize path by a factor (radii currently scale by cx)."""
    cy = cx if cy is None else cy
    for comp in path:
        if comp['command'] in ['M', 'L']:
            comp['to'] = scaled_point(comp['to'], cx, cy)
        elif comp['command'] == 'C':
            comp['c1'] = scaled_point(comp['c1'], cx, cy)
            comp['c2'] = scaled_point(comp['c2'], cx, cy)
            comp['to'] = scaled_point(comp['to'], cx, cy)
        elif comp['command'] == 'A':
            comp['r'] *= abs(cx)
            if cx * cy < 0:
                comp['positive'] = not comp['positive']
            comp['to'] = scaled_point(comp['to'], cx, cy)
