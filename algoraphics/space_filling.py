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
from .param import Param, make_param
from .color import make_color


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


def _filament_fill_obj(bounds, direction_delta, width, seg_length, color):
    """Generate filament extending into bounds.

    Called indirectly by lambda function produced by filament_fill().

    Args:
        bounds (tuple): A bounds tuple.
        direction_delta (Param): Parameter that will become the delta for the filament direction.
        width (float|int): Width of the filament.
        seg_length (float|int): Average side length of each segment.
        color (Color): Color specification for filament segments.  A separate copy is used for each filament in case it involves deltas/ratios.

    Returns:
        list: The ordered segment polygons.

    """
    direction_delta = make_param(direction_delta)
    width = make_param(width)
    seg_length = make_param(seg_length)
    color = make_color(color)

    c = ((bounds[0] + bounds[1]) / 2., (bounds[2] + bounds[3]) / 2.)
    r = distance(c, (bounds[1], bounds[3]))
    start = rand_point_on_circle(c, r)
    angle = math.atan2(c[1] - start[1], c[0] - start[0])
    dir_start = deg(angle) + random.uniform(-60, 60)
    direction = Param(dir_start, delta=direction_delta)
    n_segments = int(2.2 * r / seg_length.mean)
    x = filament(start, direction, width, seg_length, n_segments)
    set_style(x, 'fill', color)
    return x


def filament_fill(direction_delta, width, seg_length, color):
    """Generate filament fill function.

    Args:
        direction_delta (Param): Parameter that will become the delta for the filament direction.
        width (float|int): Width of the filament.
        seg_length (float|int): Average side length of each segment.
        color (Color): Color specification for filament segments.  A separate copy is used for each filament in case it involves deltas/ratios.

    Returns:
        function: A function used by fill_region().

    """
    return lambda bounds: _filament_fill_obj(bounds, direction_delta,
                                             width, seg_length, color)
