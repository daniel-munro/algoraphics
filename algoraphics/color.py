"""
color.py
========
Functions for working with colors.

"""

import numpy as np
import colorsys
import matplotlib.colors
from typing import Union, Tuple, Sequence

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
    def __init__(self, hsl: Tuple[float, float, float] = None, hue:
                 float = None, sat: float = None, li: float = None,
                 rgb: Tuple[float, float, float] = None, RGB:
                 Tuple[int, int, int] = None):
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
    # else:
    #     TODO error

# def rgb_to_hsl(rgb):
#     """Convert RGB tuple to HSL tuple."""
#     h, l, s = colorsys.rgb_to_hls(rgb[0] / 255., rgb[1] / 255., rgb[2] / 255.)
#     return (h, s, l)


# def hsl_to_rgb(hsl):
#     """Convert HSL tuple to RGB tuple."""
#     r, g, b = colorsys.hls_to_rgb(hsl[0], hsl[2], hsl[1])
#     return (int(r * 255), int(g * 255), int(b * 255))


# def hex_to_rgb(hx):
#     """Convert hex color to RGB tuple."""
#     if len(hx) == 4:
#         hx = hx[0] + 2 * hx[1] + 2 * hx[2] + 2 * hx[3]
#     rgb = matplotlib.colors.hex2color(hx)
#     return tuple([int(255 * x) for x in rgb])


# def hex_to_hsl(hx):
#     """Convert hex color to HSL tuple."""
#     return rgb_to_hsl(hex_to_rgb(hx))


def rgb_array_to_hsv(rgb: np.ndarray) -> np.ndarray:
    """Convert matrix of rgb values to HSV.

    Args:
        rgb: An array of rgb colors.

    Returns:
        An array of HSV colors.
    """
    # return matplotlib.colors.rgb_to_hsv(rgb / 255)
    return matplotlib.colors.rgb_to_hsv(rgb)


def hsv_array_to_rgb(hsv: np.ndarray) -> np.ndarray:
    """Convert matrix of HSV values to rgb.

    Args:
        hsv: An array of HSV colors.

    Returns:
        An array of rgb colors.
    """
    return matplotlib.colors.hsv_to_rgb(hsv)


# def rand_col_nearby(color, hue_tol, sat_tol, light_tol):
#     """Select random color within range of reference color.

#     Args:
#         color (tuple): An RGB tuple.
#         hue_tol (float): Maximum hue deviation, usually 0 to 0.5.
#         sat_tol (float): Maximum saturation deviation, usually 0 to 1.
#         light_tol (float): Maximum lightness deviation, usually 0 to 1.

#     Returns:
#         tuple: An RGB tuple.

#     """
#     hue, sat, li = rgb_to_hsl(color)
#     hue = random.uniform(hue - hue_tol, hue + hue_tol) % 1
#     sat = random.uniform(sat - sat_tol, sat + sat_tol)
#     sat = max(0, min(sat, 1))
#     li = random.uniform(li - light_tol, li + light_tol)
#     li = max(0, min(li, 1))
#     return hsl_to_rgb((hue, sat, li))


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
        new_light = min(hsl[2] + light_diff, 1.)
    else:
        new_light = max(hsl[2] - light_diff, 0.)
    new_hsl = (hsl[0], hsl[1], new_light)
    return Color(hsl=new_hsl)


# def color_mixture(color1, color2, proportion=0.5, mode='rgb'):
#     """Get mixture of two colors at specified proportion.

#     Args:
#         color1 (tuple): An RGB or HSL tuple.
#         color2 (tuple): An RGB or HSL tuple, must match type of color1.
#         proportion (float): Fraction of mixture coming from color2.
#         mode (str): Either 'rgb' or 'hsl'.

#     Returns:
#         tuple: An RGB or HSL tuple.

#     """
#     if mode == 'rgb':
#         r = color1[0] + int(proportion * (color2[0] - color1[0]))
#         g = color1[1] + int(proportion * (color2[1] - color1[1]))
#         b = color1[2] + int(proportion * (color2[2] - color1[2]))
#         return (r, g, b)

#     elif mode == 'hsl':
#         h1 = color1[0]
#         h2 = color2[0]
#         if h2 - h1 > 0.5:
#             h1 += 1
#         elif h1 - h2 > 0.5:
#             h2 += 1
#         h = (h1 + proportion * (h2 - h1)) % 1
#         s = color1[1] + proportion * (color2[1] - color1[1])
#         li = color1[2] + proportion * (color2[2] - color1[2])
#         return (h, s, li)


def map_colors_to_array(values: np.ndarray, colors: Sequence[Color],
                        gradient_mode: str = 'rgb') -> np.ndarray:
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
    if gradient_mode == 'hsv':
        colors = rgb_array_to_hsv(np.array([colors]))[0, :]

    # Get the two colors per pixel to be mixed:
    color1 = values.astype(int)
    color2 = ((values + 1) % len(colors)).astype(int)
    proportion = values % 1
    c1 = colors[color1]
    c2 = colors[color2]

    if gradient_mode == 'rgb':
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
    out = (out * 255).astype('uint8')
    return out
