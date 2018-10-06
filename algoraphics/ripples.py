"""
ripples.py
==========
Create space-filling ripple effects.

"""

import numpy as np

from .main import add_margin, markov_next, set_style
from .geom import rotated_point, rad, endpoint, distance, Rtree


def next_point(points, spacing, mode):
    """Continue from last two elements of points."""
    last = points.points[-2:]
    if mode == 'r':
        angle = 60
        angle_inc = 5
        stop_angle = 300
        newpt_fun = lambda ang: rotated_point(last[-2], last[-1], rad(ang))
    elif mode == 'l':
        angle = 300
        angle_inc = -5
        stop_angle = 60
        newpt_fun = lambda ang: rotated_point(last[-2], last[-1], rad(ang))
    elif mode == 's':
        angle = np.random.choice(range(360))
        direction = np.random.choice([-1, 1])
        angle_inc = direction * 1
        stop_angle = angle + direction * 359
        newpt_fun = lambda ang: endpoint(last[-1], angle, spacing)
    elif mode == 'x':
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


# def scan_for_space(bounds, points, spacing):
#     precision = 5
#     xvals = np.arange(bounds[0], bounds[1], precision)
#     yvals = np.arange(bounds[2], bounds[3], precision)
#     for x in np.random.permutation(xvals):
#         for y in np.random.permutation(yvals):
#             neighbors = [p for p in points if distance((x, y), p) <= spacing * 2]
#             if len(neighbors) <= 5:  # <= 5 still has space somewhere to go
#                 too_close = [p for p in neighbors if distance((x, y), p) <= spacing]
#                 if len(too_close) == 0:
#                     return (x, y)
#     return None


# def scan_for_space(open_space, points, spacing):
#     print('search...')
#     while len(open_space) > 0:
#         newpt = open_space.pop()
#         neighbors = [p for p in points if distance(newpt, p) <= spacing * 2]
#         if len(neighbors) <= 5:  # <= 5 still has space somewhere to go
#             too_close = [p for p in neighbors if distance(newpt, p) <= spacing]
#             if len(too_close) == 0:
#                 print('done')
#                 return newpt
#     return None


def scan_for_space(open_space, points, spacing):
    # print('search...')
    while len(open_space) > 0:
        newpt = open_space.pop()
        neighbors = points.nearest(newpt, 6)
        # <= 5 in vicinity still has space somewhere to go
        if distance(newpt, neighbors[-1]) >= spacing * 2:
            if distance(newpt, neighbors[0]) >= spacing:
                # print('done')
                return newpt
    return None


def ripple_canvas(w, h, spacing, trans_probs=None, existing_pts=None):
    if trans_probs is None:
        trans_probs = dict(s=dict(r=1), r=dict(r=1))

    margin = 3
    bounds = add_margin((0, w, 0, h), margin)

    curves = []  # list of list of points that will become paths
    allpts = Rtree(existing_pts)  # for finding neighbors

    pts = [(x, bounds[2]) for x in np.arange(bounds[0], bounds[1], spacing)]
    pts.extend([(bounds[1], y) for y in
                np.arange(bounds[2], bounds[3], spacing)])
    pts.extend([(x, bounds[3]) for x in
                np.arange(bounds[1], bounds[0], -spacing)])
    pts.extend([(bounds[0], y) for y in
                np.arange(bounds[3], bounds[2], -spacing)])
    curves.append(pts)
    allpts.add_points(pts)

    precision = 5
    xvals = np.arange(bounds[0], bounds[1], precision)
    yvals = np.arange(bounds[2], bounds[3], precision)
    open_space = [(x, y) for x in xvals for y in yvals]
    np.random.shuffle(open_space)

    start = scan_for_space(open_space, allpts, spacing)
    pts = [start]
    allpts.add_point(start)

    mode = 's'
    more_space = True
    while more_space:
        newpt = next_point(allpts, spacing, mode)
        if newpt is not None:
            pts.append(newpt)
            allpts.add_point(newpt)
            mode = markov_next(mode, trans_probs)
        else:
            curves.append(pts)
            new_start = scan_for_space(open_space, allpts, spacing)
            if new_start is not None:
                pts = [new_start]
                allpts.add_point(new_start)
                mode = 's'
            else:
                more_space = False

    paths = [dict(type='spline', points=p) for p in curves]
    set_style(paths, 'fill', 'none')
    set_style(paths, 'stroke', 'black')
    return paths
