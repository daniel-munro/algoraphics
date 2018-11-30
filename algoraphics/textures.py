"""
textures.py
===========
Add textures and shadows to shapes.

"""

import numpy as np

from .main import add_margin, bounding_box, random_walk
from .color import map_colors_to_array, make_color
from .images import array_to_image
from .grid import grid_tree_dists
from .param import fixed_value


def add_shadows(objects, stdev=10, darkness=0.5):
    """Add shadows to objects.

    Each element (nested or not) of the list is replaced with a group
    with shadow filter. So items that are shapes will have their own
    shadow, while an item that is a (nested) list of shapes will have
    one shadow for the composite object.

    Args:
        objects (list): A list of objects (can be nested).
        stdev (float|int): Standard deviation of shadow gradient.
        darkness (float|int): A number below one for lighter shadow, above one for darker.

    """
    for i, obj in enumerate(objects):
        obj = obj if isinstance(obj, list) else [obj]
        fltr = dict(type='shadow', stdev=stdev, darkness=darkness)
        objects[i] = dict(type='group', members=obj, filter=fltr)


def with_shadow(obj, stdev, darkness):
    """Add shadow to an object.

    Like add_shadows() but returns a group with a single shadow filter.

    Args:
        object (dict|list): A shape or list of objects (can be nested).
        stdev (float|int): Standard deviation of shadow gradient.
        darkness (float|int): A number below one for lighter shadow, above one for darker.

    Returns:
        A group with `obj` as members and filter applied to group.

    """
    return filtered(obj, dict(type='shadow', stdev=stdev, darkness=darkness))


def filtered(obj, fltr):
    """Apply filter to object.

    Args:
        obj (dict|list): A shape or (nested) list.
        fltr (dict): A filter.

    Returns:
        dict: A group with `obj` as members and filter applied to group.

    """
    obj = obj if isinstance(obj, list) else [obj]
    return dict(type='group', members=obj, filter=fltr)


def billowing(w, h, colors, scale, gradient_mode='rgb'):
    """Generate a billowing texture.

    Args:
        w (int): Width of the texture.
        h (int): Height of the texture.
        colors (list): A list of Color objects to cycle through.
        scale (int): Distance in pixels for each color cycle.
        gradient_mode (str): 'rgb' or 'hsl' to choose the appearance of the gradient.

    Returns:
        Image: A PIL image object (i.e. not a dict).

    """
    dists = grid_tree_dists(rows=h, cols=w)
    values = ((dists % scale) / scale) * len(colors)
    mat = map_colors_to_array(values, colors, scale, gradient_mode)
    return array_to_image(mat)


def billow_region(outline, colors, scale=200, gradient_mode='rgb'):
    """Fill region with billowing texture.

    Args:
        outline (dict|list): The object that will become the clip.
        colors (list): A list of Colors to cycle through.
        scale (int): The distance in pixels for each color cycle.
        gradient_mode (str): 'rgb' or 'hsl' to indicate how the gradient is interpolated.

    Returns:
        dict: A group with clip.

    """
    colors = [make_color(color) for color in colors]
    scale = fixed_value(scale)

    bound = add_margin(bounding_box(outline), 2)
    w = int(bound[1] - bound[0])
    h = int(bound[3] - bound[2])
    billow = billowing(w, h, colors, scale, gradient_mode)
    billow = dict(type='raster', image=billow, x=bound[0], y=bound[2],
                  format='PNG')
    return dict(type='group', clip=outline, members=[billow])


def add_paper_texture(obj):
    """Recursively apply paper texture to objects.

    Args:
        obj (dict|list): A shape or (nested) list of shapes.

    """
    if isinstance(obj, list):
        for o in obj:
            add_paper_texture(o)
    elif obj['type'] == 'group':
        for o in obj['members']:
            add_paper_texture(o)
    else:
        obj['filter'] = dict(type='roughness')


def tear_paper_rect(objects, bounds):
    """Add effect of tearing a rectangle around an object.

    Args:
        objects (dict|list): A shape or (nested) list of shapes.
        bounds (tuple): A rectangle will be torn just inside these bounds.

    Returns:
        dict: A shadow-filtered group containing a clipped group
        containing original shapes.

    """
    e = 10
    d = 0.5

    s1 = (bounds[0] + np.random.uniform(0, e),
          bounds[2] + np.random.uniform(0, e))
    s = s1
    points = [s]
    n = int((bounds[1] - s[0] - np.random.uniform(0, e)) / d)
    x = [s[0] + d * i for i in range(n)]
    y = random_walk(min_val=bounds[2], max_val=bounds[2] + e,
                    max_step=0.5, n=n, start=s[1])
    points.extend(zip(x, y))

    s = points[-1]
    n = int((bounds[3] - s[1] - np.random.uniform(0, e)) / d)
    x = random_walk(min_val=bounds[1] - e, max_val=bounds[1],
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

    clip = dict(type='polygon', points=points)
    members = objects if isinstance(objects, list) else [objects]
    group = dict(type='group', clip=clip, members=members)
    return filtered(group, dict(type='shadow', stdev=7, darkness=0.8))
