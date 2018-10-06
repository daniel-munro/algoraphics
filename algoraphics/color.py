"""
color.py
========
Functions for working with colors.

"""

import numpy as np
import random
import colorsys
import matplotlib.colors


def rgb_to_hsl(rgb):
    """Convert RGB tuple to HSL tuple."""
    h, l, s = colorsys.rgb_to_hls(rgb[0] / 255., rgb[1] / 255., rgb[2] / 255.)
    return (h, s, l)


def hsl_to_rgb(hsl):
    """Convert HSL tuple to RGB tuple."""
    r, g, b = colorsys.hls_to_rgb(hsl[0], hsl[2], hsl[1])
    return (int(r * 255), int(g * 255), int(b * 255))


def hex_to_rgb(hx):
    """Convert hex color to RGB tuple."""
    if len(hx) == 4:
        hx = hx[0] + 2 * hx[1] + 2 * hx[2] + 2 * hx[3]
    rgb = matplotlib.colors.hex2color(hx)
    return tuple([int(255 * x) for x in rgb])


def hex_to_hsl(hx):
    """Convert hex color to HSL tuple."""
    return rgb_to_hsl(hex_to_rgb(hx))


def rgb_to_hsv(rgb):
    """Convert matrix of RGB values to HSV."""
    return matplotlib.colors.rgb_to_hsv(rgb / 255)


def hsv_to_rgb(hsv):
    """Convert matrix of HSV values to RGB."""
    return (matplotlib.colors.hsv_to_rgb(hsv) * 255).astype('uint8')


def rand_col_from_ranges(r, g, b):
    """Select random color from possible RGB components.

    Each argument is a number from 0 to 255 or a list of numbers to randomly
    choose from, e.g. produced from range(40, 200).

    Returns:
        An RGB tuple.

    """
    result = []
    for x in (r, g, b):
        if not isinstance(x, list):
            x = [x]
        result.append(random.choice(x))
    return tuple(result)


def rand_col_nearby(color, hue_tol, sat_tol, light_tol):
    """Select random color within range of reference color.

    Args:
        color (tuple): An RGB tuple.
        hue_tol (float): Maximum hue deviation, usually 0 to 0.5.
        sat_tol (float): Maximum saturation deviation, usually 0 to 1.
        light_tol (float): Maximum lightness deviation, usually 0 to 1.

    Returns:
        An RGB tuple.

    """
    hue, sat, li = rgb_to_hsl(color)
    hue = random.uniform(hue - hue_tol, hue + hue_tol) % 1
    sat = random.uniform(sat - sat_tol, sat + sat_tol)
    sat = max(0, min(sat, 1))
    li = random.uniform(li - light_tol, li + light_tol)
    li = max(0, min(li, 1))
    return hsl_to_rgb((hue, sat, li))


def average_color(colors):
    """Find average of list of colors.

    Args:
        colors (list): A list of RGB tuples.

    Returns:
        An RGB tuple.

    """
    colors = np.array(colors)
    return tuple([int(np.mean(colors[:, i])) for i in range(3)])


def contrasting_lightness(color, light_diff):
    """Get color with contrasting lightness to reference color.

    Color is lighter if original lightness is < 0.5 and darker otherwise.
    Used to create color pairs for a mixture of light and dark colors.

    Args:
        color (tuple): An RGB tuple.
        light_diff (float): Magnitude of difference in lightness, between 0 and 1.

    Returns:
        An RGB tuple.

    """
    hsl = rgb_to_hsl(color)
    if hsl[2] < 0.5:
        new_light = min(hsl[2] + light_diff, 1.)
    else:
        new_light = max(hsl[2] - light_diff, 0.)
    new_hsl = (hsl[0], hsl[1], new_light)
    return hsl_to_rgb(new_hsl)


def color_mixture(color1, color2, proportion=0.5, mode='rgb'):
    """Get mixture of two colors at specified proportion.

    Args:
        color1 (tuple): An RGB or HSL tuple.
        color2 (tuple): An RGB or HSL tuple, must match type of color1.
        proportion (float): Fraction of mixture coming from color2.
        mode (str): Either 'rgb' or 'hsl'.

    Returns:
        An RGB or HSL tuple.

    """
    if mode == 'rgb':
        r = color1[0] + int(proportion * (color2[0] - color1[0]))
        g = color1[1] + int(proportion * (color2[1] - color1[1]))
        b = color1[2] + int(proportion * (color2[2] - color1[2]))
        return (r, g, b)

    elif mode == 'hsl':
        h1 = color1[0]
        h2 = color2[0]
        if h2 - h1 > 0.5:
            h1 += 1
        elif h1 - h2 > 0.5:
            h2 += 1
        h = (h1 + proportion * (h2 - h1)) % 1
        s = color1[1] + proportion * (color2[1] - color1[1])
        li = color1[2] + proportion * (color2[2] - color1[2])
        return (h, s, li)


def map_to_gradient(values, colors, period, gradient_mode='rgb'):
    """Map 2D array of values to cyclical color gradient.

    Used when values are pixel distances, producing a cyclical color
    gradient.  Outputs in RGB mode regardless of mode specified for
    gradient.

    Args:
        values (numpy.ndarray): A 2D array.
        colors (list): A list of RGB colors.
        period (float|int): The range of values covered by gradient before it repeats.
        gradient_mode (str): Either 'rgb' or 'hsv'. This changes the appearance of the color gradient, but input and output colors are in RGB regardless.

    Returns:
        A 3D array of RGB values.

    """
    if gradient_mode == 'hsv':
        colors = [rgb_to_hsv(np.array([[c]]))[0, 0, :] for c in colors]

    values = np.array(values) % period / period * len(colors)
    color1 = values.astype(int)
    color2 = ((values + 1) % len(colors)).astype(int)
    proportion = values % 1
    c1 = np.array(colors)[color1]
    c2 = np.array(colors)[color2]
    if gradient_mode == 'rgb':
        out = c1 + proportion[:, :, np.newaxis] * (c2 - c1)
    else:
        h1 = c1[:, :, 0]
        h2 = c2[:, :, 0]
        h1[h2 - h1 > 0.5] += 1
        h2[h1 - h2 > 0.5] += 1
        h = (h1 + proportion * (h2 - h1)) % 1
        out = c1 + proportion[:, :, np.newaxis] * (c2 - c1)
        out[:, :, 0] = h
        out = hsv_to_rgb(out)

    out = out.astype('uint8')
    return out
