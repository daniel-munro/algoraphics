"""
textures.py
===========
Add textures to shapes.

"""

import numpy as np
from typing import Union, Sequence
from PIL import Image
from typing import Tuple

from ..main import add_margin, bounding_box
from ..color import map_colors_to_array, make_color, Color
from ..grid import grid_tree_dists
from ..param import fixed_value

Collection = Union[list, dict]


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


def billowing(
    w: int, h: int, colors: Sequence[Color], scale: int, gradient_mode: str = "rgb"
) -> "Image":
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


def billow_region(
    outline: Collection,
    colors: Sequence[Color],
    scale: int = 200,
    gradient_mode: str = "rgb",
) -> dict:
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
    billow = dict(type="raster", image=billow, x=bound[0], y=bound[1], format="PNG")
    return dict(type="group", clip=outline, members=[billow])
