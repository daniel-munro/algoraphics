import numpy as np
from .main import *
from .geom import *
from .text import points_on_line


def next_point(points, spacing, mode):
    """continue from last two elements of points"""
    if mode == 'r':
        angle = 60
        angle_inc = 1
        stop_angle = 300
        newpt_fun = lambda ang: rotated_point(points[-2], points[-1], rad(ang))
    elif mode == 'l':
        angle = 300
        angle_inc = -1
        stop_angle = 60
        newpt_fun = lambda ang: rotated_point(points[-2], points[-1], rad(ang))
    elif mode == 'x':
        angle = np.random.choice(range(360))
        angle_inc = np.random.choice([-1, 1])
        stop_angle = angle + angle_inc * 359
        newpt_fun = lambda ang: endpoint(points[-1], angle, spacing)

    neighbors = [p for p in points[:-1] if distance(points[-1], p) <= spacing * 2]
    while True:
        newpt = newpt_fun(angle)
        if len([p for p in neighbors if distance(newpt, p) < spacing]) == 0:
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


def scan_for_space(open_space, points, spacing):
    print('search...')
    while len(open_space) > 0:
        newpt = open_space.pop()
        neighbors = [p for p in points if distance(newpt, p) <= spacing * 2]
        if len(neighbors) <= 5:  # <= 5 still has space somewhere to go
            too_close = [p for p in neighbors if distance(newpt, p) <= spacing]
            if len(too_close) == 0:
                print('done')
                return newpt
    return None


def scan_for_space(open_space, points, spacing):
    print('search...')
    while len(open_space) > 0:
        newpt = open_space.pop()
        neighbors = [p for p in points if distance(newpt, p) <= spacing * 2]
        if len(neighbors) <= 5:  # <= 5 still has space somewhere to go
            too_close = [p for p in neighbors if distance(newpt, p) <= spacing]
            if len(too_close) == 0:
                print('done')
                return newpt
    return None


def ripple_canvas(w, h, spacing, trans_probs=None, existing_pts=None):
    if trans_probs is None:
        trans_probs = dict(x=dict(r=1), r=dict(r=1))

    margin = 0
    bounds = add_margin((0, w, 0, h), margin)

    curves = []  # list of list of points that will become paths
    if existing_pts is None:
        allpts = []  # flat list to easily find neighbors
    else:
        allpts = existing_pts

    pts = [(x, bounds[2]) for x in np.arange(bounds[0], bounds[1], spacing)]
    pts.extend([(bounds[1], y) for y in np.arange(bounds[2], bounds[3], spacing)])
    pts.extend([(x, bounds[3]) for x in np.arange(bounds[1], bounds[0], -spacing)])
    pts.extend([(bounds[0], y) for y in np.arange(bounds[3], bounds[2], -spacing)])
    curves.append(pts)
    allpts.extend(pts)

    center = (w / 2, h / 2)
    angle = rad(np.random.choice(range(360)))
    pts = [center]
    allpts.append(center)

    precision = 5
    xvals = np.arange(bounds[0], bounds[1], precision)
    yvals = np.arange(bounds[2], bounds[3], precision)
    open_space = [(x, y) for x in xvals for y in yvals]
    np.random.shuffle(open_space)

    mode = 'x'
    more_space = True
    while more_space:
        newpt = next_point(allpts, spacing, mode)
        if newpt is not None:
            pts.append(newpt)
            allpts.append(newpt)
            mode = markov_next(mode, trans_probs)
        else:
            curves.append(pts)
            new_start = scan_for_space(open_space, allpts, spacing)
            if new_start is not None:
                pts = [new_start]
                allpts.append(new_start)
                mode = 'x'
            else:
                more_space = False

    paths = [dict(type='spline', points=p, \
                  style=dict(fill='none', stroke='red')) for p in curves]
    return paths
