"""
main.py
=======
General functions for creating graphics.

"""

import random
import numpy as np

from .geom import distance
from .shapes import rectangle, bounding_box
from .param import Param
from .color import Color


def set_style(obj, attribute, value):
    """Set style attribute of one or more shapes.

    Args:
        obj (dict|list): A shape or (nested) list of shapes.
        attribute (str): Name of the style attribute.
        value (str|number|function): either a single value or a function that returns values when called with no arguments.

    """
    if isinstance(obj, list):
        for o in obj:
            set_style(o, attribute, value)
    else:
        if 'style' not in obj:
            obj['style'] = dict()
        if type(value) is Param:
            obj['style'][attribute] = value.value()
        elif type(value) is Color:
            obj['style'][attribute] = value.hex()
        elif callable(value):
            obj['style'][attribute] = value()
        else:
            obj['style'][attribute] = value


def flatten(objects):
    """Create a flattened list from a nested list.

    Args:
        objects (object): A nested list or a non-list.

    Returns:
        list: The non-list elements within the input.

    """
    out = []
    if isinstance(objects, list):
        for obj in objects:
            out.extend(flatten(obj))
    else:
        out.append(objects)
    return out


def random_walk(min_val, max_val, max_step, n, start=None):
    """Generate a random walk sequence.

    Steps are sampled from a uniform random distribution.

    Args:
        min_val (float): Values will not fall below this value.
        max_val (float): Values will not fall above this value.
        max_step (flot): Maximum magnitude of each step.
        n (int): Length of the sequence.
        start (number): The starting value.

    Returns:
        list: The generated sequence.

    """
    if start is None:
        x = [random.uniform(min_val, max_val)]
    else:
        x = [float(start)]
    for i in range(1, n):
        val = x[-1] + random.uniform(-max_step, max_step)
        x.append(max(min_val, min(max_val, val)))
    return x


def shuffled(items):
    """Create shuffled version of a list.

    Args:
        items (list): A list of items.

    Returns:
        list: A new list with same objects as input but reordered.

    """
    return random.sample(items, len(items))


def arith_seq(start, stop, length):
    """Generate an arithmetic sequence.

    Args:
        start (float): The first value in the sequence.
        stop (float): The last value in the sequence.
        length (int): The length of the the sequence.

    Returns:
        list: The generated sequence.

    """
    return [(float(x) / (length - 1)) * (stop - start) + start for x
            in range(length)]


def geom_seq(start, stop, length):
    """Generate geometric sequence.

    Args:
        start (float): The first value in the sequence.
        stop (float): The last value in the sequence.
        length (int): Length of the sequence.

    Returns:
        list: The generated sequence.

    """
    r = (float(stop) / start) ** (1. / (length - 1))
    return [start * (r ** i) for i in range(length)]


def reorder_objects(objects, by='random', w=None, h=None):
    """Reorder objects in list.

    Used to change order in which objects are drawn.

    Args:
        objects (list): A list whose items are shapes or lists.
        by (str): 'random' to shuffle objects.  'out to in' to arrange objects closer to the center on top of (later in list) those further from the center.  Distance is determined by furthest corner of bounding box so that smaller objects tend to be arranged on top of larger ones that surround them.
        w (float|int): Canvas width, used to get center when by='out to in'.
        h (float|int): Canvas height, used to get center when by='out to in'.

    """
    if by == 'random':
        random.shuffle(objects)

    elif by == 'out to in':
        center = (w / 2., h / 2.)

        def key_fun(obj):
            b = bounding_box(obj)
            # c = ((b[1] + b[0]) / 2., (b[3] + b[2]) / 2.)
            # return distance(center, c)
            d1 = distance(center, (b[0], b[2]))
            d2 = distance(center, (b[0], b[3]))
            d3 = distance(center, (b[1], b[2]))
            d4 = distance(center, (b[1], b[3]))
            return max(d1, d2, d3, d4)
        objects.sort(key=key_fun, reverse=True)


def add_margin(bounds, margin):
    """Add margin to bounds.

    A convenience function used when generating objects to avoid
    issues at the edges of the region or canvas.

    Args:
        bounds (tuple): A tuple of min x, max x, min y, and max y.
        margin (float|int): The width of the margin.

    Returns:
        tuple: Bounds that include the margin on all sides.

    """
    return (bounds[0] - margin, bounds[1] + margin,
            bounds[2] - margin, bounds[3] + margin)


def background(fill, w, h, margin=0):
    """Create a background color for the canvas.

    See region_background to set background for a specific region.

    Args:
        fill (color): The background color.
        w (int): width of canvas.
        h (int): height of canvas.
        margin (int): width of margin to include to avoid edge artifacts.

    Returns:
        tuple: A filled rectangular polygon covering the canvas.

    """
    bg = rectangle(bounds=(-margin, w + margin, -margin, h + margin))
    set_style(bg, 'fill', fill)
    return bg


def region_background(region, color):
    """Add background color to clipped region.

    Adds a filled rectangle to the beginning of the region's members.

    Args:
        region (dict): A clipped group object.
        color (color|function): A color or function to apply to the region.

    """
    bounds = add_margin(bounding_box(region['clip']), 10)
    bg = rectangle(bounds=bounds)
    set_style(bg, 'fill', color)
    if isinstance(region['members'], list):
        region['members'].insert(0, bg)
    else:
        region['members'] = [bg, region['members']]


def tint_region(region, color, opacity):
    bounds = add_margin(bounding_box(region['clip']), 10)
    tint = rectangle(bounds=bounds)
    set_style(tint, 'fill', color)
    set_style(tint, 'opacity', opacity)
    if isinstance(region['members'], list):
        region['members'].append(tint)
    else:
        region['members'] = [region['members'], tint]


def _markov_next(state, trans_probs):
    """Get the next state in a first-order Markov chain.

    Args:
        state (str): The current state.
        trans_probs (dict): A dictionary of dictionaries containing transition probabilities from one state (first key) to another (second key).

    Returns:
        str: The next state.

    """
    states = list(trans_probs[state].keys())
    probs = [trans_probs[state][s] for s in states]
    return np.random.choice(states, p=probs)
