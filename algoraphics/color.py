"""
color.py
========
Functions for working with colors.

"""

import numpy as np
import colorsys
from typing import Sequence, Tuple, Union

from .param import fixed_value, make_param


class Color:
    """Object to represent a color or distribution of colors.

    Define using either an hsl tuple, separate
    hue/saturation/lightness arguments, or an RGB tuple.  Any
    component can be a Param object.

    Args:
        hsl: The hsl specification, where each component is between 0 and 1.
        hue: The hue specification from 0 to 1.  sat and li must also
          be provided.
        sat: The saturation specification from 0 to 1.
        li: The lightness specification from 0 to 1.
        RGB: The red/green/blue components, each ranging from 0 to 255.

    """

    def __init__(
        self,
        # hsl: Tuple[float, float, float] = None,
        hue: float = None,
        sat: float = None,
        li: float = None,
        RGB: Tuple[int, int, int] = None,
    ):
        if hue is not None:
            assert sat is not None and li is not None
        # elif hsl is not None:
        #     self.hsl = hsl
        elif RGB is not None:
            r, g, b = tuple([fixed_value(x) / 255 for x in RGB])
            hue, li, sat = colorsys.rgb_to_hls(r, g, b)
        self.hue = make_param(hue)
        self.sat = make_param(sat)
        self.li = make_param(li)

    def __str__(self):
        return "Color({}, {}, {})".format(self.hue, self.sat, self.li)

    def hsl(self, t: int = 0) -> Tuple[float, float, float]:
        """Get the color's hsl specification.

        Returns the specification at time t if the color is parameterized.

        """
        hue = self.hue.state(t)
        sat = self.sat.state(t)
        li = self.li.state(t)
        return (hue % 1, np.clip(sat, 0, 1), np.clip(li, 0, 1))

    def rgb(self, t: int = 0) -> Tuple[float, float, float]:
        """Get the color's rgb specification.

        Returns the specification at time t if the color is parameterized.

        """
        # from https://en.wikipedia.org/wiki/HSL_and_HSV#HSL_to_RGB
        # (could have used colorsys, but I might switch to HCL.
        hue, sat, li = self.hsl(t)
        c = (1 - abs(2*li - 1)) * sat  # chroma
        h = hue * 6
        x = c * (1 - abs((h % 2) - 1))
        if 0 <= h and h <= 1:
            rgb1 = (c, x, 0)
        elif 1 <= h and h <= 2:
            rgb1 = (x, c, 0)
        elif 2 <= h and h <= 3:
            rgb1 = (0, c, x)
        elif 3 <= h and h <= 4:
            rgb1 = (0, x, c)
        elif 4 <= h and h <= 5:
            rgb1 = (x, 0, c)
        elif 5 <= h and h <= 6:
            rgb1 = (c, 0, x)
        m = li - c / 2
        return (rgb1[0] + m, rgb1[1] + m, rgb1[2] + m)

    def state(self, t: int = 0) -> str:
        """Get the color's hex specification.

        Returns one fixed specification if the color is parameterized.

        """
        rgb = self.rgb(t)
        R, G, B = tuple([int(round(x * 255)) for x in rgb])
        return "#{0:02x}{1:02x}{2:02x}".format(R, G, B)


def make_color(x: Union[Color, Tuple[float, float, float]]) -> Color:
    """Convert to a color object if a tuple (assumed to be hsl) is provided."""
    if isinstance(x, Color):
        return x
    elif type(x) is tuple:
        return Color(*x)
    else:
        raise ValueError("Colors must be Color objects or length 3 tuples.")


def average_color(colors: Sequence[Color]) -> Color:
    """Find average of list of colors.

    This finds the arithmetic mean in RGB color space, since averaging
    hues has unexpected results with black, white, and gray.

    Args:
        colors: A list of Color objects.

    Returns:
        The average color.

    """
    reds, greens, blues = zip(*[make_color(color).rgb() for color in colors])
    rgb = (np.mean(reds), np.mean(greens), np.mean(blues))
    RGB = tuple([int(round(x * 255)) for x in rgb])
    return Color(RGB=RGB)
