"""
svg.py
======
write SVG files.

"""

import numpy as np
import string
import subprocess
import os
import cairosvg
from PIL import Image
from io import BytesIO
from base64 import b64encode
from typing import Union, Sequence, Callable, Tuple

from .main import flatten
from .geom import endpoint, rotated_point, direction_to, distance, rad
from .shapes import scale_shapes, translate_shapes, rectangle
from .color import Color

Number = Union[int, float]
Point = Tuple[Number, Number]


class Canvas:
    def __init__(self, width, height, background="white"):
        self.width = width
        self.height = height
        self.objects = []
        self.background = background
        # I could cache the SVG string, but how to know if it needs to
        # be updated?
        # self.svg = None

    def add(self, *object: Union[list, dict]):
        for obj in object:
            self.objects.append(obj)

    def clear(self):
        self.objects = []

    def new(self, *object):
        self.objects = []
        self.add(*object)

    def get_svg(self):
        obj = self.objects[:]
        if self.background is not None:
            bg = rectangle(
                bounds=(-1, -1, self.width + 1, self.height + 1), fill=self.background
            )
            obj.insert(0, bg)
        return svg_string(obj, self.width, self.height)

    def svg(self, file_name: str, optimize: bool = True):
        """Write the canvas to an SVG file.

        Args:
            file_name: The file name to write to.
            optimize: Whether to optimize the SVG file using svgo.

        """
        svg = self.get_svg()
        open(file_name, "w").write(svg)
        if optimize:
            subprocess.run(["svgo", "--quiet", "--precision=2", "--input=" + file_name])

    def png(self, file_name: str):
        svg = self.get_svg()
        cairosvg.svg2png(svg, write_to=file_name)


def _encode_image(image: Image, frmt: str) -> str:
    """Encode an image as a data string.

    Used to embed images in SVG.

    Args:
        image: A PIL Image.
        frmt: Either 'JPEG' or 'PNG'.

    Returns:
        The image encoding.

    """
    formats = dict(JPEG="jpg", PNG="png")
    enc = BytesIO()
    image.save(enc, format=frmt)
    data = b64encode(enc.getvalue()).decode("utf-8")
    return "data:image/" + formats[frmt] + ";base64," + data


def _match_dict(dicts: Sequence[dict], d: dict) -> Union[int, None]:
    """Return index of dict in ``dicts`` matching ``d``.

    Returns None if no match.

    """
    for i in range(len(dicts)):
        if dicts[i] == d:
            return i
    return None


def _spline_path(
    points: Sequence[Point], smoothing: float = 0.2, circular: bool = False
) -> str:
    """Generate path string for spline.

    Args:
        points: A list of points.
        smoothing: The distance to the control point relative to the
          distance to the adjacent point. Usually between zero and
          one.
        circular: If False, spline ends reasonably at the first and
          last points.  If True, the ends of the spline will connect
          smoothly.

    Returns:
        An SVG path.

    """
    # Add reference points at ends, which don't get drawn:
    if circular:
        points = [points[-1]] + points + [points[0], points[1]]
    else:
        p0 = rotated_point(points[1], points[0], np.pi)
        p_last = rotated_point(points[-2], points[-1], np.pi)
        points = [p0] + points + [p_last]

    path = "M {} {}".format(*points[1])

    direction = direction_to(points[0], points[2])
    dist = distance(points[0], points[2])
    c1 = endpoint(points[1], rad(direction), smoothing * dist)

    direction = direction_to(points[3], points[1])
    dist = distance(points[3], points[1])
    c2 = endpoint(points[2], rad(direction), smoothing * dist)
    path += "C {} {} {} {} {} {}".format(*c1, *c2, *points[2])

    for i in range(3, len(points) - 1):
        direction = direction_to(points[i + 1], points[i - 1])
        dist = distance(points[i + 1], points[i - 1])
        c = endpoint(points[i], rad(direction), smoothing * dist)
        path += "S {} {} {} {}".format(*c, *points[i])
    return path


def _write_polygon(shape: dict, mods: str) -> str:
    """Generate the SVG representation of a polygon."""
    points = " ".join([str(x[0]) + "," + str(x[1]) for x in shape["points"]])
    return '<polygon points="' + points + '" ' + mods + "/>\n"


def _write_spline(shape: dict, mods: str) -> str:
    """Generate the SVG representation of a spline path."""
    if "smoothing" not in shape:
        shape["smoothing"] = 0.2
    if "circular" not in shape:
        shape["circular"] = False
    d = _spline_path(shape["points"], shape["smoothing"], shape["circular"])
    return '<path d="' + d + '" ' + mods + "/>\n"


def _write_circle(shape: dict, mods: str) -> str:
    """Generate the SVG representation of a circle."""
    return (
        '<circle cx="'
        + str(shape["c"][0])
        + '" cy="'
        + str(shape["c"][1])
        + '" r="'
        + str(shape["r"])
        + '" '
        + mods
        + "/>\n"
    )


def _write_line(shape: dict, mods: str) -> str:
    """Generate the SVG representation of a line."""
    return (
        '<line x1="'
        + str(shape["p1"][0])
        + '" y1="'
        + str(shape["p1"][1])
        + '" x2="'
        + str(shape["p2"][0])
        + '" y2="'
        + str(shape["p2"][1])
        + '" '
        + mods
        + "/>\n"
    )


def _write_polyline(shape: dict, mods: str) -> str:
    """Generate the SVG representation of a polyline."""
    points = " ".join([str(x[0]) + "," + str(x[1]) for x in shape["points"]])
    return '<polyline points="' + points + '" fill="none" ' + mods + "/>\n"


def _write_text(shape: dict, mods: str) -> str:
    """Generate SVG text."""
    anchors = dict(left="start", center="middle", right="end")
    anchor = anchors[shape["align"]]
    return (
        '<text x="'
        + str(shape["x"])
        + '" y="'
        + str(shape["y"])
        + '" '
        + 'text-anchor="'
        + anchor
        + '" '
        + 'font-size="'
        + str(shape["font_size"])
        + '" '
        + mods
        + ">"
        + shape["text"]
        + "</text>\n"
    )


def _write_raster(shape: dict, mods: str) -> str:
    """Generate the SVG representation of a raster image."""
    output = "<image "
    if "w" not in shape:
        shape["w"] = shape["image"].width
    if "h" not in shape:
        shape["h"] = shape["image"].height
    if "x" in shape:
        output += 'x="' + str(shape["x"]) + '" '
    if "y" in shape:
        output += 'y="' + str(shape["y"]) + '" '
    output += (
        'width="'
        + str(shape["w"])
        + '" height="'
        + str(shape["h"])
        + '" xlink:href="'
        + _encode_image(shape["image"], shape["format"])
        + '" '
        + mods
        + "/>\n"
    )
    return output


def _write_group(
    shape: dict, mods: str, defs: Sequence[str], filters: Sequence[dict]
) -> str:
    """Generate an SVG group."""
    output = "<g "
    if "clip" in shape:
        clip_id = "".join(np.random.choice(list(string.ascii_letters), 8))
        clip = '<clipPath id="' + clip_id + '">\n'
        clip += "".join(
            [_write_shape(o, defs, filters) for o in flatten(shape["clip"])]
        )
        clip += "</clipPath>\n"
        defs.append(clip)
        output += 'clip-path="url(#' + clip_id + ')" '
    output += mods + ">\n"
    output += "".join(
        [_write_shape(o, defs, filters) for o in flatten(shape["members"])]
    )
    output += "</g>\n"
    return output


def _write_shape(shape: dict, defs: Sequence[str], filters: Sequence[dict]) -> str:
    """Generate SVG representation of a shape.

    Args:
        shape: A geometric shape, group, text, or raster dictionary.
        defs: A list of strings used to collect SVG representations of
          all clip paths, filters, etc.
        filters: A collection of filter dictionaries used thus far so
          that duplicate filters can reference the same definition.

    Returns:
        An SVG encoding.

    """
    style_string = 'style="' + _write_style(shape) + '" '

    if "filter" in shape:
        match = _match_dict(filters, shape["filter"])
        if match is None:
            filters.append(shape["filter"])
            match = len(filters) - 1
        filter_id = "filter" + str(match)
        filter_string = 'filter="url(#' + filter_id + ')" '
    else:
        filter_string = ""

    mods = style_string + filter_string

    draw_funs = dict(
        polygon=_write_polygon,
        spline=_write_spline,
        circle=_write_circle,
        line=_write_line,
        polyline=_write_polyline,
        text=_write_text,
        raster=_write_raster,
    )

    if shape["type"] == "group":
        output = _write_group(shape, mods, defs, filters)
    else:
        output = draw_funs[shape["type"]](shape, mods)

    return output


def _write_style(shape: dict) -> str:
    """Generate an SVG representation of a shape's style.

    Args:
        shape: A geometric shape, group, text, or raster dictionary.

    Returns:
        An SVG encoding which should be inserted between the quotes of
        style="...".

    """
    if "style" in shape:
        style = shape["style"].copy()  # Keep input dict intact for reuse.
    else:
        style = dict()
    if shape["type"] in ("spline", "circle", "polygon") and "fill" not in style:
        style["fill"] = "none"
        if "stroke" not in style:
            style["stroke"] = "black"
    if shape["type"] in ("line", "polyline") and "stroke" not in style:
        style["stroke"] = "black"
    if "fill" in style and type(style["fill"]) is tuple:
        RGB = Color(hsl=style["fill"]).RGB()
        style["fill"] = "rgb(" + ", ".join([str(x) for x in RGB]) + ")"
    if "stroke" in style and type(style["stroke"]) is tuple:
        RGB = Color(hsl=style["stroke"]).RGB()
        style["stroke"] = "rgb(" + ", ".join([str(x) for x in RGB]) + ")"

    if "stroke" in style and style["stroke"] == "match":
        # 'match' used to slightly expand filled shapes by setting the
        # stroke to match the fill.  Useful to prevent gap artifacts.
        if "fill" in style:
            style["stroke"] = style["fill"]
        else:
            del style["stroke"]

    # Originally I used '_' in place of '-' so that style could be
    # set with dict(), but I don't think it's worth the confusion.  if
    # not using set_style, the dictionary could always be set with
    # {}.
    # style = [(prop.replace("_", "-"), value) for prop, value in style.items()]
    # return ';'.join([prop + ':' + str(value) for prop, value in style])
    return ";".join([prop + ":" + str(value) for prop, value in style.items()])


def _write_filters(filters: Sequence[dict]) -> str:
    """Generate an SVG representation of all filters used in a graphic.

    Args:
        filters: A list of filters.

    Returns:
        An SVG encoding.

    """
    fltrs = []
    for i, fltr in enumerate(filters):

        if fltr["type"] == "shadow":
            f = '<filter id="filter' + str(i) + '" '
            f += 'x="-50%" y="-50%" width="200%" height="200%">\n'

            f += '<feGaussianBlur in="SourceAlpha" '
            f += 'stdDeviation="' + str(fltr["stdev"]) + '" result="blur" />\n'

            f += (
                '<feFlood flood-color="black" flood-opacity="'
                + str(fltr["darkness"])
                + '" />\n'
            )
            f += '<feComposite in2="blur" operator="in" />\n'

            f += (
                "<feMerge>"
                + '<feMergeNode /><feMergeNode in="SourceGraphic" />'
                + "</feMerge>\n"
            )
            f += "</filter>\n"

        elif fltr["type"] == "roughness":
            f = '<filter id="filter' + str(i) + '">\n'
            f += (
                '<feTurbulence type="fractalNoise" baseFrequency="0.02" '
                + 'numOctaves="5" result="noise" />\n'
            )
            f += (
                '<feDiffuseLighting in="noise" lighting-color="white" '
                + 'surfaceScale="0.5" result="diffLight">\n'
            )
            f += '<feDistantLight azimuth="45" elevation="35" />\n'
            f += "</feDiffuseLighting>\n"

            f += (
                '<feColorMatrix in="diffLight" type="matrix" '
                + 'values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  1 0 0 0 0" '
                + 'result="diffLightLight" />\n'
            )
            f += (
                '<feColorMatrix in="diffLight" type="matrix" '
                + 'values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -1 0 0 0 1" '
                + 'result="diffLightShadow" />\n'
            )

            f += (
                '<feComponentTransfer in="diffLightLight" '
                + 'result="diffLightLight2">\n'
            )
            f += '<feFuncA type="table" tableValues="0 0 0.8" />\n'
            f += "</feComponentTransfer>\n"

            f += (
                '<feComponentTransfer in="diffLightShadow" '
                + 'result="diffLightShadow2">\n'
            )
            f += '<feFuncA type="table" tableValues="0 0 0.5 0.5" />\n'
            f += "</feComponentTransfer>\n"

            f += (
                '<feComposite in2="SourceGraphic" in="diffLightShadow2" '
                + 'operator="atop" result="sourceWithShadow" />\n'
            )
            f += (
                '<feComposite in2="sourceWithShadow" in="diffLightLight2" '
                + 'operator="atop" />\n'
            )
            f += "</filter>\n"

        fltrs.append(f)
    return fltrs


def write_SVG(
    objects: Union[list, dict],
    w: Number,
    h: Number,
    file_name: str,
    optimize: bool = True,
):
    """Write an SVG file for a collection of objects.

    Args:
        objects: A (nested) collection of objects.  They are placed
          onto the canvas in order after flattening.
        w: Width of canvas.
        h: Height of canvas.
        file_name: The file name to write to.
        optimize: Whether to optimize the SVG file using svgo.

    """
    defs = []
    filters = []
    out = '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" '
    out += 'xmlns:xlink="http://www.w3.org/1999/xlink" '
    out += 'width="' + str(w) + '" height="' + str(h) + '">\n'

    # flip y-axis so zero is at the bottom:
    scale_shapes(objects, 1, -1)
    translate_shapes(objects, 0, h)

    objects = "".join([_write_shape(obj, defs, filters) for obj in flatten(objects)])

    defs.extend(_write_filters(filters))
    out += "<defs>\n" + "".join(defs) + "</defs>\n"

    # flip y-axis so zero is at the bottom:
    # out += '<g transform="translate(0, ' + str(h) + ') scale(1, -1)">\n'
    # out += objects
    # out += '</g>\n</svg>\n'
    out += objects + "</svg>\n"

    open(file_name, "w").write(out)
    if optimize:
        subprocess.run(
            [
                "svgo",
                "--quiet",
                "--precision=2",
                # '--config=/home/dan/coding/graphics/algoraphics/scripts/svgo_config.txt',
                # '--disable=collapseGroups',
                "--input=" + file_name,
            ]
        )


def svg_string(objects: Union[list, dict], w: Number, h: Number):
    """Create an SVG string for a collection of objects.

    Args:
        objects: A (nested) collection of objects.  They are placed
          onto the canvas in order after flattening.
        w: Width of the canvas.
        h: Height of the canvas.

    """
    defs = []
    filters = []
    out = '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" '
    out += 'xmlns:xlink="http://www.w3.org/1999/xlink" '
    out += 'width="' + str(w) + '" height="' + str(h) + '">\n'

    # flip y-axis so zero is at the bottom:
    scale_shapes(objects, 1, -1)
    translate_shapes(objects, 0, h)

    objects = "".join([_write_shape(obj, defs, filters) for obj in flatten(objects)])

    defs.extend(_write_filters(filters))
    out += "<defs>\n" + "".join(defs) + "</defs>\n"

    out += objects + "</svg>\n"
    return out


def to_PNG(infile: str, outfile: str = None):
    """Convert and SVG file to a PNG image.

    Args:
        infile: The SVG file name.
        outfile: The PNG file name to write to.  If omitted, it will
          be set to the SVG file name with the extension replaced with
          '.png'.

    """
    if outfile is None:
        inbase = os.path.splitext(infile)[0]
        outfile = inbase + ".png"
    subprocess.run(["convert", infile, outfile])


def write_frames(fun: Callable, n: int, w: Number, h: Number, file_name: str):
    """Write multiple frames of randomized objects.

    Frames can then be combined into an animated GIF.

    Args:
        fun: A function called with no arguments that returns an SVG
          object collection.
        n: Number of frames to generate.
        w: Width of the canvas.
        h: Height of the canvas.
        file_name: A file name (without extension) to write to.  File
          names will be [file_name]_0.svg, etc.

    """
    for i in range(n):
        write_SVG(fun(), w, h, file_name + "_" + str(i) + ".svg")


# For assembling GIF:
# convert -dither None -delay 5 $1_*.svg -clone 0 -morph 1 -delete -1 $1.gif

# def round_values(obj, digits=0):
#     """rounds all values in nested structure"""
#
#     def round_value(value, digits=0):
#         if digits == 0:
#             return int(round(value))
#         else:
#             return round(value, digits)
#
#     def process_item(obj, i):
#         if isinstance(obj[i], (list, dict)):
#             round_values(obj[i], digits)
#         elif isinstance(obj[i], float):
#             obj[i] = round_value(obj[i], digits)
#
#     if isinstance(obj, list):
#         for i in range(len(obj)):
#             process_item(obj, i)
#     else:
#         for field in obj:
#             process_item(obj, field)
