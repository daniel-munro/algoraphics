"""
space_filling.py
================
Fill regions by iteratively placing randomly generated objects.

"""

import math
import random

from .main import add_margin, bounding_box, coverage, flatten, remove_hidden
from .main import set_style
from .geom import distance, rand_point_on_circle, deg
from .filaments import filament


def fill_region(outline, object_fun, max_tries=None):
    """Fill a region by iteratively placing randomly generated objects.

    Args:
        outline (dict|list): A shape or (nested) list of shapes that will become clip.
        object_fun (function): A function that takes bounds as input and returns one randomly generated object.  Usually this is a lambda function that calls another function using arguments passed to the function that produced the lambda function.  i.e., def caller_fun(args...): return lambda bounds: helper_fun(bounds, args...)
        max_tries (int): If not None, the number of objects to generate (including those discarded for not filling space) before giving up and returning the region as is.

    Returns:
        dict: A group with clip.

    """
    bounds = add_margin(bounding_box(outline), 10)
    space = coverage(outline)
    objects = []
    try_count = 0
    while space.area > 0.1 and (max_tries is None or try_count < max_tries):
        try_count += 1
        obj = object_fun(bounds)
        # space_copy = copy.deepcopy(space)
        old_area = space.area
        shapes = [coverage(o) for o in flatten(obj)]
        for shape in shapes:
            space = space.difference(shape)
        if space.area < old_area:
            objects.append(obj)
            # space = space_copy

    filled_region = dict(type='group', clip=outline, members=objects)
    remove_hidden(filled_region)
    return filled_region


def filament_fill_obj(bounds, color_fun, width, l_min, l_max, l_max_step):
    """Generate filament extending into bounds.

    Called indirectly by lambda function produced by filament_fill().

    Args:
        bounds (tuple): A bounds tuple.
        color_fun (function): Called for each segment to get fill color.
        width (float|int): Width of filament.
        l_min (float|int): Minimum side length of segment.
        l_max (float|int): Maximum side length of segment.
        l_max_step (float|int): If not None, the edge lengths on each side of the filament will be determined by random walk, and this will be the maximum step size.

    Returns:
        list: The ordered segment polygons.

    """
    c = ((bounds[0] + bounds[1]) / 2., (bounds[2] + bounds[3]) / 2.)
    r = distance(c, (bounds[1], bounds[3]))
    start = rand_point_on_circle(c, r)
    angle = math.atan2(c[1] - start[1], c[0] - start[0])
    direction = deg(angle) + random.uniform(-60, 60)
    segments = int(2.2 * r / ((l_min + l_max) / 2.))
    x = filament(start, direction, width, l_min, l_max, segments, l_max_step)
    set_style(x, 'fill', color_fun)
    return x


def filament_fill(color_fun, width, l_min, l_max, l_max_step=None):
    """Generate filament fill function.

    Args:
        color_fun (function): Called for each segment to get fill color.
        width (float|int): Width of the filament.
        l_min (float|int): Minimum side length of a segment.
        l_max (float|int): Maximum side length of a segment.
        l_max_step (float|int): If not None, the edge lengths on each side of the filament will be determined by a random walk, and this will be the maximum step size.

    Returns:
        function: A function used by fill_region().

    """
    return lambda bounds: filament_fill_obj(bounds, color_fun, width,
                                            l_min, l_max, l_max_step)
