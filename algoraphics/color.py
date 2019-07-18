"""
color.py
========
Functions for working with colors.

"""

import numpy as np
import colorsys
import matplotlib.colors
from typing import Sequence, Tuple, Union

from .param import fixed_value


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
        hsl: Tuple[float, float, float] = None,
        hue: float = None,
        sat: float = None,
        li: float = None,
        RGB: Tuple[int, int, int] = None,
    ):
        if hue is not None:
            assert sat is not None and li is not None
            self.hsl = (hue, sat, li)
        elif hsl is not None:
            self.hsl = hsl
        elif RGB is not None:
            r, g, b = tuple([fixed_value(x) / 255 for x in RGB])
            hue, li, sat = colorsys.rgb_to_hls(r, g, b)
            self.hsl = (hue, sat, li)

    def __str__(self):
        return str(self.hsl)

    def value(self) -> Tuple[float, float, float]:
        """Get the color's hsl specification.

        Returns one fixed specification if the color is parameterized.

        """
        hue, sat, li = tuple([fixed_value(x) for x in self.hsl])
        return (hue % 1, np.clip(sat, 0, 1), np.clip(li, 0, 1))

    def rgb(self) -> Tuple[float, float, float]:
        """Get the color's rgb specification.

        Returns one fixed specification if the color is parameterized.

        """
        # from https://en.wikipedia.org/wiki/HSL_and_HSV#HSL_to_RGB
        # (could have used colorsys, but I might switch to HCL.
        hue, sat, li = self.value()
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

    def hex(self) -> str:
        """Get the color's hex specification.

        Returns one fixed specification if the color is parameterized.

        """
        rgb = self.rgb()
        R, G, B = tuple([int(round(x * 255)) for x in rgb])
        return "#{0:02x}{1:02x}{2:02x}".format(R, G, B)


def make_color(x: Union[Color, Tuple[float, float, float]]) -> Color:
    """Convert to a color object if a tuple (assumed to be hsl) is provided."""
    if isinstance(x, Color):
        return x
    elif type(x) is tuple:
        return Color(hsl=x)
    else:
        raise ValueError("Colors must be Color objects or length 3 tuples.")


def rgb_array_to_hsv(rgb: np.ndarray) -> np.ndarray:
    """Convert matrix of rgb values to HSV.

    Args:
        rgb: An array of rgb colors.

    Returns:
        An array of HSV colors.
    """
    return matplotlib.colors.rgb_to_hsv(rgb)


def hsv_array_to_rgb(hsv: np.ndarray) -> np.ndarray:
    """Convert matrix of HSV values to rgb.

    Args:
        hsv: An array of HSV colors.

    Returns:
        An array of rgb colors.
    """
    return matplotlib.colors.hsv_to_rgb(hsv)


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


def map_colors_to_array(
    values: np.ndarray, colors: Sequence[Color], gradient_mode: str = "rgb"
) -> np.ndarray:
    """Map 2D array of values to a cyclical color gradient.

    If values vary continuously in space, this produces a cyclical color
    gradient.

    Args:
        values: A 2D array of floats.  Values should range from 0,
          inclusive, to len(colors) + 1, exclusive.  Each value
          corresponds to a proportional mixture of the colors at the
          two indices it is between (with values higher than the last
          index cycling back to the first color).
        colors: A list of Color objects.
        gradient_mode: Either 'rgb' or 'hsv' to indicate how the
          colors are interpolated.

    Returns:
        A 3D array of RGB values (RGB mode because this is used for
        PIL images).

    """
    colors = np.array([make_color(color).rgb() for color in colors])
    if gradient_mode == "hsv":
        colors = rgb_array_to_hsv(np.array([colors]))[0, :]

    # Get the two colors per pixel to be mixed:
    color1 = values.astype(int)
    color2 = ((values + 1) % len(colors)).astype(int)
    proportion = values % 1
    c1 = colors[color1]
    c2 = colors[color2]

    if gradient_mode == "rgb":
        # Weighted average for each of R, G, and B:
        out = c1 + proportion[:, :, np.newaxis] * (c2 - c1)
    else:
        # For HSL, average hue should be in direction where hues are closer:
        h1 = c1[:, :, 0]
        h2 = c2[:, :, 0]
        h1[h2 - h1 > 0.5] += 1
        h2[h1 - h2 > 0.5] += 1
        h = (h1 + proportion * (h2 - h1)) % 1
        # Weighted average for each of H, S, and L:
        out = c1 + proportion[:, :, np.newaxis] * (c2 - c1)
        out[:, :, 0] = h
        out = hsv_array_to_rgb(out)
    out = (out * 255).astype("uint8")
    return out
