"""
textures.py
===========
Add textures and shadows to shapes.

"""

import numpy as np
from typing import Union, Sequence
from PIL import Image
from typing import Tuple

from .main import add_margin, bounding_box, random_walk
from .color import map_colors_to_array, make_color, Color
from .grid import grid_tree_dists
from .param import fixed_value
from .shapes import polygon

Number = Union[int, float]
Collection = Union[list, dict]
Bounds = Tuple[Number, Number, Number, Number]


def array_to_image(array: np.ndarray, scale: bool = True) -> "Image":
    """Create an image from a 2D or 3D array.

    Args:
        array: A numpy array: 2D for grayscale or 3D for RGB.
        scale: If True, values in 2D array will be scaled so that the
          highest values are 255 (white).

    Returns:
        A PIL Image in RGB mode.

    """
    if scale and len(array.shape) == 2:
        array = 255.0 * array / np.max(array)
    if len(array.shape) == 2:
        return Image.fromarray(array).convert("RGB")
    else:
        return Image.fromarray(array, mode="RGB")


def add_shadows(objects: Sequence[Collection], stdev: Number = 10,
                darkness: Number = 0.5):
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
        fltr = dict(type='shadow', stdev=stdev, darkness=darkness)
        objects[i] = dict(type='group', members=obj, filter=fltr)


def with_shadow(obj: Collection, stdev: Number, darkness: Number) -> dict:
    """Add shadow to an object.

    Like add_shadows() but returns a group with a single shadow filter.

    Args:
        obj: A shape or list of objects (can be nested).
        stdev: Standard deviation of shadow gradient.
        darkness: A number below one for lighter shadow, above one for darker.

    Returns:
        A group with ``obj`` as members and a filter applied to the group.

    """
    return filtered(obj, dict(type='shadow', stdev=stdev, darkness=darkness))


def filtered(obj: Collection, fltr: dict) -> dict:
    """Apply a filter to one or more shapes.

    Args:
        obj: A shape or (nested) list.
        fltr: A filter.

    Returns:
        A group with ``obj`` as members and filter applied to group.

    """
    obj = obj if isinstance(obj, list) else [obj]
    return dict(type='group', members=obj, filter=fltr)


def billowing(w: int, h: int, colors: Sequence[Color], scale: int,
              gradient_mode: str = 'rgb') -> 'Image':
    """Generate a billowing texture.

    Args:
        w: Width of the texture.
        h: Height of the texture.
        colors: A list of Color objects to cycle through.
        scale: Distance in pixels for each color cycle.
        gradient_mode: 'rgb' or 'hsl' to choose the appearance of the gradient.

    Returns:
        A PIL image object.

    """
    dists = grid_tree_dists(rows=int(h), cols=int(w))
    values = ((dists % scale) / scale) * len(colors)
    mat = map_colors_to_array(values, colors, gradient_mode)
    return array_to_image(mat)


def billow_region(outline: Collection, colors: Sequence[Color], scale:
                  int = 200, gradient_mode: str = 'rgb') -> dict:
    """Fill region with billowing texture.

    Args:
        outline: The object that will become the clip.
        colors: A list of Colors to cycle through.
        scale: The distance in pixels for each color cycle.
        gradient_mode: 'rgb' or 'hsl' to indicate how the gradient is
          interpolated.

    Returns:
        A group with clip.

    """
    colors = [make_color(color) for color in colors]
    scale = fixed_value(scale)

    bound = add_margin(bounding_box(outline), 2)
    w = int(bound[2] - bound[0])
    h = int(bound[3] - bound[1])
    billow = billowing(w, h, colors, scale, gradient_mode)
    billow = dict(type='raster', image=billow, x=bound[0], y=bound[1],
                  format='PNG')
    return dict(type='group', clip=outline, members=[billow])


def add_paper_texture(obj: Collection):
    """Recursively apply paper texture to shapes.

    Args:
        obj: A shape or (nested) list of shapes.

    """
    if isinstance(obj, list):
        for o in obj:
            add_paper_texture(o)
    elif obj['type'] == 'group':
        for o in obj['members']:
            add_paper_texture(o)
    else:
        obj['filter'] = dict(type='roughness')


def tear_paper_rect(objects: Collection, bounds: Bounds) -> dict:
    """Add effect of tearing a rectangle around a shape or collection.

    Args:
        objects: A shape or (nested) list of shapes.
        bounds: A rectangle will be torn just inside these bounds.

    Returns:
        A shadow-filtered group containing a clipped group containing
        original shapes.

    """
    e = 10
    d = 0.5

    s1 = (bounds[0] + np.random.uniform(0, e),
          bounds[1] + np.random.uniform(0, e))
    s = s1
    points = [s]
    n = int((bounds[2] - s[0] - np.random.uniform(0, e)) / d)
    x = [s[0] + d * i for i in range(n)]
    y = random_walk(min_val=bounds[1], max_val=bounds[1] + e,
                    max_step=0.5, n=n, start=s[1])
    points.extend(zip(x, y))

    s = points[-1]
    n = int((bounds[3] - s[1] - np.random.uniform(0, e)) / d)
    x = random_walk(min_val=bounds[2] - e, max_val=bounds[2],
                    max_step=0.5, n=n, start=s[0])
    y = [s[1] + d * i for i in range(n)]
    points.extend(zip(x, y))

    s = points[-1]
    n = int((s[0] - bounds[0] - np.random.uniform(0, e)) / d)
    x = [s[0] - d * i for i in range(n)]
    y = random_walk(min_val=bounds[3] - e, max_val=bounds[3],
                    max_step=0.5, n=n, start=s[1])
    points.extend(zip(x, y))

    s = points[-1]
    n = int((s[1] - s1[1]) / d)
    x = random_walk(min_val=bounds[0], max_val=bounds[0] + e,
                    max_step=0.5, n=n, start=s[0])
    y = [s[1] - d * i for i in range(n)]
    points.extend(zip(x, y))

    clip = polygon(points=points)
    members = objects if isinstance(objects, list) else [objects]
    group = dict(type='group', clip=clip, members=members)
    return filtered(group, dict(type='shadow', stdev=7, darkness=0.8))
