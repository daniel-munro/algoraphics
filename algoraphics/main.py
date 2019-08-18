"""
main.py
=======
General functions for creating graphics.

"""

import numpy as np
from typing import Union, Any, Sequence, Tuple

from .geom import distance
from .shapes import rectangle, bounding_box, Shape, Group
from .color import Color

# Number = Union[int, float]
Collection = Union[Shape, Group, list]
# Bounds = Tuple[Number, Number, Number, Number]
Bounds = Tuple[float, float, float, float]


def flatten(objects: Any) -> list:
    """Create a flattened list from a nested list.

    Args:
        objects: A nested list or a non-list.

    Returns:
        The non-list elements within the input.

    """
    out = []
    if type(objects) is list:
        for obj in objects:
            out.extend(flatten(obj))
    else:
        out.append(objects)
    return out


def shuffled(items: Sequence) -> list:
    """Create shuffled version of a list.

    Args:
        items: A list of items.

    Returns:
        A new list with same objects as input but reordered.

    """
    return list(np.random.choice(items, len(items), replace=False))


def reorder_objects(
    objects: Sequence[Collection],
    by: str = "random",
    w: float = None,
    h: float = None,
):
    """Reorder objects in list.

    Used to change order in which objects are drawn.

    Args:
        objects: A list whose items are shapes or lists.
        by: 'random' to shuffle objects.  'out to in' to arrange
          objects closer to the center on top of (later in list) those
          further from the center.  Distance is determined by furthest
          corner of bounding box so that smaller objects tend to be
          arranged on top of larger ones that surround them.
        w: Canvas width, used to get center when by='out to in'.
        h: Canvas height, used to get center when by='out to in'.

    """
    if by == "random":
        np.random.shuffle(objects)

    elif by == "out to in":
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


def add_margin(bounds: Bounds, margin: float) -> Bounds:
    """Add margin to bounds.

    A convenience function used when generating objects to avoid
    issues at the edges of the region or canvas.

    Args:
        bounds: A tuple of min x, min y, max x, and max y.
        margin: The width of the margin.

    Returns:
        Bounds that include the margin on all sides.

    """
    return (
        bounds[0] - margin,
        bounds[1] - margin,
        bounds[2] + margin,
        bounds[3] + margin,
    )


def region_background(region: dict, color: Color):
    """Add background color to a clipped region.

    Adds a filled rectangle to the beginning of the region's members.

    Args:
        region: A clipped group shape.
        color: A color to apply to the region.

    """
    bounds = add_margin(bounding_box(region.clip), 10)
    bg = rectangle(bounds=bounds, fill=color)
    region.members.insert(0, bg)


def add_shadows(
    objects: Sequence[Collection], stdev: float = 10, darkness: float = 0.5
):
    """Add shadows to objects.

    Each element (nested or not) of the list is replaced with a group
    with shadow filter. So items that are shapes will have their own
    shadow, while an item that is a (nested) list of shapes will have
    one shadow for the composite object.

    Args:
        objects: A list of shapes (can be nested).
        stdev: Standard deviation of the shadow gradient.
        darkness: A number below one for lighter shadow, above one for darker.

    """
    for i, obj in enumerate(objects):
        obj = obj if isinstance(obj, list) else [obj]
        fltr = dict(type="shadow", stdev=stdev, darkness=darkness)
        objects[i] = Group(members=obj, filter=fltr)


def with_shadow(obj: Collection, stdev: float, darkness: float) -> dict:
    """Add shadow to an object.

    Like add_shadows() but returns a group with a single shadow filter.

    Args:
        obj: A shape or list of objects (can be nested).
        stdev: Standard deviation of shadow gradient.
        darkness: A number below one for lighter shadow, above one for darker.

    Returns:
        A group with ``obj`` as members and a filter applied to the group.

    """
    return filtered(obj, dict(type="shadow", stdev=stdev, darkness=darkness))


def filtered(obj: Collection, fltr: dict) -> dict:
    """Apply a filter to one or more shapes.

    Args:
        obj: A shape or (nested) list.
        fltr: A filter.

    Returns:
        A group with ``obj`` as members and filter applied to group.

    """
    obj = obj if isinstance(obj, list) else [obj]
    return Group(members=obj, filter=fltr)
