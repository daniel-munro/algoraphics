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

    Define using any of an hsl tuple, separate
    hue/saturation/lightness arguments, an rgb tuple (0 to 1), or an
    RGB tuple (integers 0 to 255).  Any component can be a Param
    object.

    Args:
        hsl: The hsl specification, where each component is between 0 and 1.
        hue: The hue specification from 0 to 1.  sat and li must also
          be provided.
        sat: The saturation specification from 0 to 1.
        li: The lightness specification from 0 to 1.
        rgb: The red/green/blue components, each ranging from 0 to 1.
        RGB: The red/green/blue components, each ranging from 0 to 255.

    """

    def __init__(
        self,
        hsl: Tuple[float, float, float] = None,
        hue: float = None,
        sat: float = None,
        li: float = None,
        rgb: Tuple[float, float, float] = None,
        RGB: Tuple[int, int, int] = None,
    ):
        if hue is not None:
            assert sat is not None and li is not None
            self.hsl = (hue, sat, li)
        elif hsl is not None:
            self.hsl = hsl
        elif rgb is not None:
            hue, li, sat = colorsys.rgb_to_hls(*rgb)
            self.hsl = (hue, sat, li)
        elif RGB is not None:
            r, g, b = tuple([x / 255 for x in RGB])
            hue, li, sat = colorsys.rgb_to_hls(r, g, b)
            self.hsl = (hue, sat, li)

    def value(self) -> Tuple[float, float, float]:
        """Get the color's hsl specification.

        Returns one fixed specification if the color is parameterized.

        """
        return tuple([fixed_value(x) for x in self.hsl])

    def hex(self) -> str:
        """Get the color's hsl specification.

        Returns one fixed specification if the color is parameterized.

        """
        return matplotlib.colors.to_hex(self.rgb())

    def rgb(self) -> Tuple[float, float, float]:
        """Get the color's rgb specification.

        Returns one fixed specification if the color is parameterized.

        """
        hsl = self.value()
        return colorsys.hls_to_rgb(hsl[0], hsl[2], hsl[1])

    def RGB(self) -> Tuple[int, int, int]:
        """Get the color's RGB specification.

        Returns one fixed specification if the color is parameterized.

        """
        r, g, b = self.rgb()
        return (int(r * 255), int(g * 255), int(b * 255))


def make_color(x: Union[Color, Tuple[float, float, float]]) -> Color:
    """Convert to a color object if a tuple is provided."""
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

    Currently, this finds the arithmetic mean in RGB color space.

    Args:
        colors: A list of Color objects.

    Returns:
        The average color.

    """
    rgbs = [make_color(color).rgb() for color in colors]
    rgb = tuple([np.mean(component) for component in zip(*rgbs)])
    return Color(rgb=rgb)


def contrasting_lightness(color: Color, light_diff: float) -> Color:
    """Get color with contrasting lightness to reference color.

    Color is lighter if original lightness is < 0.5 and darker otherwise.
    Used to create color pairs for a mixture of light and dark colors.

    Args:
        color: A color.
        light_diff: Magnitude of difference in lightness, between 0 and 1.

    Returns:
        The contrasting color.

    """
    hsl = make_color(color).value()
    if hsl[2] < 0.5:
        new_light = min(hsl[2] + light_diff, 1.0)
    else:
        new_light = max(hsl[2] - light_diff, 0.0)
    new_hsl = (hsl[0], hsl[1], new_light)
    return Color(hsl=new_hsl)


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
