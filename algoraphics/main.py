"""
main.py
=======
General functions for creating graphics.

"""

import numpy as np
from typing import Union, Callable, Any, Sequence, Dict, Tuple

from .geom import distance
from .shapes import rectangle, bounding_box
from .param import Param
from .color import Color

Number = Union[int, float]
Collection = Union[dict, list]
Bounds = Tuple[Number, Number, Number, Number]


def set_style(obj: Collection, attribute: str,
              value: Union[str, Number, Param, Color, Callable]):
    """Set style attribute of one or more shapes.

    Args:
        obj: A shape or (nested) list of shapes.
        attribute: Name of the style attribute.
        value: Either a single value, Color, Param, or a function that returns values when called with no arguments.

    """
    if isinstance(obj, list):
        for o in obj:
            set_style(o, attribute, value)
    else:
        if 'style' not in obj:
            obj['style'] = dict()
        if isinstance(value, Param):
            obj['style'][attribute] = value.value()
        elif type(value) is Color:
            obj['style'][attribute] = value.hex()
        elif callable(value):
            obj['style'][attribute] = value()
        else:
            obj['style'][attribute] = value


def flatten(objects: Any) -> list:
    """Create a flattened list from a nested list.

    Args:
        objects: A nested list or a non-list.

    Returns:
        The non-list elements within the input.

    """
    out = []
    if isinstance(objects, list):
        for obj in objects:
            out.extend(flatten(obj))
    else:
        out.append(objects)
    return out


def random_walk(min_val: Number, max_val: Number, max_step: Number, n:
                int, start: Number = None) -> list:
    """Generate a random walk sequence.

    Steps are sampled from a uniform random distribution.

    Args:
        min_val: Values will not fall below this value.
        max_val: Values will not fall above this value.
        max_step: Maximum magnitude of each step.
        n: Length of the sequence.
        start: The starting value.

    Returns:
        The generated sequence.

    """
    if start is None:
        x = [np.random.uniform(min_val, max_val)]
    else:
        x = [float(start)]
    for i in range(1, n):
        val = x[-1] + np.random.uniform(-max_step, max_step)
        x.append(max(min_val, min(max_val, val)))
    return x


def shuffled(items: Sequence) -> list:
    """Create shuffled version of a list.

    Args:
        items: A list of items.

    Returns:
        A new list with same objects as input but reordered.

    """
    return list(np.random.choice(items, len(items), replace=False))


def arith_seq(start: Number, stop: Number, length: int) -> list:
    """Generate an arithmetic sequence.

    Args:
        start: The first value in the sequence.
        stop: The last value in the sequence.
        length: The length of the the sequence.

    Returns:
        The generated sequence.

    """
    return [(float(x) / (length - 1)) * (stop - start) + start for x
            in range(length)]


def geom_seq(start: Number, stop: Number, length: int) -> list:
    """Generate geometric sequence.

    Args:
        start: The first value in the sequence.
        stop: The last value in the sequence.
        length: Length of the sequence.

    Returns:
        The generated sequence.

    """
    r = (float(stop) / start) ** (1. / (length - 1))
    return [start * (r ** i) for i in range(length)]


def reorder_objects(objects: Sequence[Collection], by: str = 'random',
                    w: Number = None, h: Number = None):
    """Reorder objects in list.

    Used to change order in which objects are drawn.

    Args:
        objects: A list whose items are shapes or lists.
        by: 'random' to shuffle objects.  'out to in' to arrange objects closer to the center on top of (later in list) those further from the center.  Distance is determined by furthest corner of bounding box so that smaller objects tend to be arranged on top of larger ones that surround them.
        w: Canvas width, used to get center when by='out to in'.
        h: Canvas height, used to get center when by='out to in'.

    """
    if by == 'random':
        np.random.shuffle(objects)

    elif by == 'out to in':
        center = (w / 2, h / 2)

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


def add_margin(bounds: Bounds, margin: Number) -> Bounds:
    """Add margin to bounds.

    A convenience function used when generating objects to avoid
    issues at the edges of the region or canvas.

    Args:
        bounds: A tuple of min x, min y, max x, and max y.
        margin: The width of the margin.

    Returns:
        Bounds that include the margin on all sides.

    """
    return (bounds[0] - margin, bounds[1] - margin,
            bounds[2] + margin, bounds[3] + margin)


def background(fill: Color, w: Number, h: Number, margin: Number = 1) -> dict:
    """Create a background color for the canvas.

    See region_background to set background for a specific region.

    Args:
        fill: The background color.
        w: width of canvas.
        h: height of canvas.
        margin: width of margin to include to avoid edge artifacts.

    Returns:
        A filled rectangular polygon covering the canvas.

    """
    bg = rectangle(bounds=(-margin, -margin, w + margin, h + margin))
    set_style(bg, 'fill', fill)
    return bg


def region_background(region: dict, color: Color):
    """Add background color to a clipped region.

    Adds a filled rectangle to the beginning of the region's members.

    Args:
        region: A clipped group shape.
        color: A color to apply to the region.

    """
    bounds = add_margin(bounding_box(region['clip']), 10)
    bg = rectangle(bounds=bounds)
    set_style(bg, 'fill', color)
    if isinstance(region['members'], list):
        region['members'].insert(0, bg)
    else:
        region['members'] = [bg, region['members']]


def tint_region(region: dict, color: Color, opacity: float):
    """Add color tint to a clipped region.

    Args:
        region: A clipped group shape.
        color: The tint color.
        opacity: The degree of tinting from 0 to 1.

    """
    bounds = add_margin(bounding_box(region['clip']), 10)
    tint = rectangle(bounds=bounds)
    set_style(tint, 'fill', color)
    set_style(tint, 'opacity', opacity)
    if isinstance(region['members'], list):
        region['members'].append(tint)
    else:
        region['members'] = [region['members'], tint]


def _markov_next(state: str, trans_probs: Dict[str, Dict[str, float]]) -> str:
    """Get the next state in a first-order Markov chain.

    Args:
        state: The current state.
        trans_probs: A dictionary of dictionaries containing transition probabilities from one state (first key) to another (second key).

    Returns:
        The next state.

    """
    states = list(trans_probs[state].keys())
    probs = [trans_probs[state][s] for s in states]
    return np.random.choice(states, p=probs)
