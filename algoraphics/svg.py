"""
svg.py
======
write SVG files.

"""

import numpy as np
import string
import subprocess

# import cairosvg
# import cairo
import tempfile
from moviepy.editor import ImageSequenceClip
# from inspect import signature
from typing import Union, Sequence, Callable, Tuple

from .main import flatten
from .geom import endpoint, rotated_point, direction_to, distance, rad
from .shapes import (
    scale_shapes,
    translate_shapes,
    rectangle,
    Polygon,
    Spline,
    Line,
    Circle,
    Group,
)
from .color import Color
from .param import fixed_value, Param

# Number = Union[int, float]
# Point = Tuple[Number, Number]
Pnt = Tuple[float, float]


class Canvas:
    """A rectangular space to be filled with graphics.

    Args:
        width: The canvas width.
        height: The canvas height.
        background: The background color.  If None, background will be
          transparent.

    """

    def __init__(self, width: float, height: float, background: Color = "white"):
        self.width = width
        self.height = height
        self.objects = []
        self.background = background
        self.t = 0
        # I could cache the SVG string, but how to know if it needs to
        # be updated?
        # self.svg = None

    def add(self, *object: Union[list, dict]):
        """Add one or more shapes or collections to the canvas."""
        for obj in object:
            self.objects.append(obj)

    def clear(self):
        """Remove all objects from the canvas."""
        self.objects = []

    def new(self, *object):
        """Clear the canvas and then add one or more shapes or collections."""
        self.objects = []
        self.add(*object)

    def get_svg(self) -> str:
        """Get the SVG representation of the canvas as a string."""
        # obj = self.objects[:]
        if self.background is not None and self.t == 0:
            bg = rectangle(
                bounds=(-1, -1, self.width + 1, self.height + 1), fill=self.background
            )
            self.objects.insert(0, bg)
        return svg_string(self.objects, self.width, self.height, self.t)

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

    def png(self, file_name: str, force_RGBA: bool = False):
        """Write the canvas to a PNG file.

        Args:
            file_name: The file name to write to.
            force_RGBA: Whether to write PNG in RGBA colorspace, even
              if it could be grayscale.  This is for, e.g., moviepy
              which requires all frame images to be in the same
              colorspace.

        """
        svg = self.get_svg()
        # cairosvg.svg2png(svg, write_to=file_name)
        handle, path = tempfile.mkstemp()
        open(handle, "w").write(svg)
        frmt = "PNG32:" if force_RGBA else ""
        # subprocess.run(["convert", "-background None", path, frmt + file_name])
        # For some reason it has to be this way to use '-background None':
        subprocess.run(
            "convert -background None {} {}".format(path, frmt + file_name), shell=True
        )
        # I tried writing directly to PNG, but it was much slower:
        # surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
        # ctx = cairo.Context(surface)
        # for obj in flatten(self.objects):
        #     # if "stroke" in obj.style and obj.style["stroke"] is not None:
                
        #     if type(obj) is Polygon:
        #         pts = [p.state() for p in obj.points]
        #         ctx.move_to(*pts[0])
        #         for pt in pts[1:] + [pts[0]]:
        #             ctx.line_to(*pt)
        #         ctx.stroke()
        #     elif type(obj) is Line:
        #         pts = [p.state() for p in obj.points]
        #         ctx.move_to(*pts[0])
        #         for pt in pts[1:]:
        #             ctx.line_to(*pt)
        #         ctx.stroke()
        #     surface.write_to_png(file_name)

    def _write_frames(self, n_frames: int, fps: int) -> Sequence[str]:
        files = []
        for i in range(n_frames):
            handle, path = tempfile.mkstemp(suffix=".png")
            self.png(path, force_RGBA=True)
            files.append(path)
            self.t += 1
        return files

    def gif(self, file_name: str, fps: int, n_frames: int = None, seconds: float = None):
        """Create a GIF image of a dynamic graphic.

        Args:
            file_name: The file name to write to.
            fps: Frames per second of the GIF.
            n_frames: Number of frames to generate.
            seconds: Specify length of the GIF in seconds instead of
              number of frames.

        """
        if n_frames is None:
            n_frames = seconds * fps
        files = self._write_frames(n_frames, fps)
        ImageSequenceClip(files, fps=fps).write_gif(file_name, logger=None)


def _match_dict(dicts: Sequence[dict], d: dict) -> Union[int, None]:
    """Return index of dict in ``dicts`` matching ``d``.

    Returns None if no match.

    """
    for i in range(len(dicts)):
        if dicts[i] == d:
            return i
    return None


def _spline_path(
    points: Sequence[Pnt], smoothing: float = 0.3, circular: bool = False
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
    # Add control points at the ends:
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


def _write_polygon(shape: Polygon, mods: str, t: int = 0) -> str:
    """Generate the SVG representation of a polygon."""
    pts = [pt.state(t) for pt in shape.points]
    points = " ".join(["{},{}".format(x[0], x[1]) for x in pts])
    return '<polygon points="{}" {}/>\n'.format(points, mods)


def _write_spline(shape: Spline, mods: str, t: int = 0) -> str:
    """Generate the SVG representation of a spline path."""
    pts = [pt.state(t) for pt in shape.points]
    if len(pts) < 2:
        return ""
    d = _spline_path(pts, shape.smoothing, shape.circular)
    return '<path d="{}" {}/>\n'.format(d, mods)


def _write_circle(shape: Circle, mods: str, t: int = 0) -> str:
    """Generate the SVG representation of a circle."""
    c = shape.c.state(t)
    r = fixed_value(shape.r, t)
    return '<circle cx="{}" cy="{}" r="{}" {}/>\n'.format(c[0], c[1], r, mods)


def _write_line(shape: Line, mods: str, t: int = 0) -> str:
    """Generate the SVG representation of a line or polyline."""
    pts = [pt.state(t) for pt in shape.points]
    if len(pts) == 2:
        return '<line x1="{}" y1="{}" x2="{}" y2="{}" {}/>\n'.format(
            pts[0][0], pts[0][1], pts[1][0], pts[1][1], mods
        )
    else:
        points = " ".join(["{},{}".format(x[0], x[1]) for x in shape.points])
        return '<polyline points="{}" fill="none" {}/>\n'.format(points, mods)


def _write_group(
    shape: Group, mods: str, defs: Sequence[str], filters: Sequence[dict], t: int = 0
) -> str:
    """Generate an SVG group."""
    output = "<g "
    if len(shape.clip) > 0:
        clip_id = "".join(np.random.choice(list(string.ascii_letters), 8))
        clip = '<clipPath id="' + clip_id + '">\n'
        clip += "".join([_write_shape(o, defs, filters) for o in flatten(shape.clip)])
        clip += "</clipPath>\n"
        defs.append(clip)
        output += 'clip-path="url(#' + clip_id + ')" '
    output += mods + ">\n"
    output += "".join(
        [_write_shape(o, defs, filters, t) for o in flatten(shape.members)]
    )
    output += "</g>\n"
    return output


def _write_shape(
    shape: dict, defs: Sequence[str], filters: Sequence[dict], t: int = 0
) -> str:
    """Generate SVG representation of a shape.

    Args:
        shape: A geometric shape or group.
        defs: A list of strings used to collect SVG representations of
          all clip paths, filters, etc.
        filters: A collection of filter dictionaries used thus far so
          that duplicate filters can reference the same definition.

    Returns:
        An SVG encoding.

    """
    if type(shape) is Group and shape.filter is not None:
        match = _match_dict(filters, shape.filter)
        if match is None:
            filters.append(shape.filter)
            match = len(filters) - 1
        filter_id = "filter" + str(match)
        filter_string = 'filter="url(#' + filter_id + ')" '
    else:
        filter_string = ""

    draw_funs = {
        "<class 'algoraphics.shapes.Polygon'>": _write_polygon,
        "<class 'algoraphics.shapes.Spline'>": _write_spline,
        "<class 'algoraphics.shapes.Circle'>": _write_circle,
        "<class 'algoraphics.shapes.Line'>": _write_line,
    }
    if type(shape) is Group:
        output = _write_group(shape, filter_string, defs, filters, t)
    else:
        style_string = 'style="' + _write_style(shape, t) + '" '
        mods = style_string + filter_string
        output = draw_funs[str(type(shape))](shape, mods, t)

    return output


def _write_style(shape: dict, t: int = 0) -> str:
    """Generate an SVG representation of a shape's style.

    Args:
        shape: A geometric shape or group.

    Returns:
        An SVG encoding which should be inserted between the quotes of
        style="...".

    """
    style = shape.style.copy()  # Keep input dict intact for reuse.
    if type(shape) in (Polygon, Spline, Circle) and "fill" not in style:
        style["fill"] = "none"
        if "stroke" not in style:
            style["stroke"] = "black"
    if type(shape) is Line and "stroke" not in style:
        style["stroke"] = "black"
    if "fill" in style and type(style["fill"]) is tuple:
        # RGB = Color(hsl=style["fill"]).RGB()
        # style["fill"] = "rgb(" + ", ".join([str(x) for x in RGB]) + ")"
        style["fill"] = Color(*style["fill"]).state()
    # elif "fill" in style and type(style["fill"]) is Color:
    #     style["fill"] = style["fill"].hex()
    if "stroke" in style and type(style["stroke"]) is tuple:
        # RGB = Color(hsl=style["stroke"]).RGB()
        # style["stroke"] = "rgb(" + ", ".join([str(x) for x in RGB]) + ")"
        style["stroke"] = Color(*style["stroke"]).state()
    # elif "stroke" in style and type(style["stroke"]) is Color:
    #     style["stroke"] = style["stroke"].hex()
    if "stroke" in style and style["stroke"] == "match":
        # 'match' used to slightly expand filled shapes by setting the
        # stroke to match the fill.  Useful to prevent gap artifacts.
        if "fill" in style:
            style["stroke"] = style["fill"]
        else:
            del style["stroke"]

    for sty in style.keys():
        if isinstance(style[sty], Param) or type(style[sty]) is Color:
            style[sty] = style[sty].state(t)

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
        fltrs.append(f)
    return fltrs


def svg_string(objects: Union[list, dict], w: float, h: float, t: int = 0):
    """Create an SVG string for a collection of objects.

    Args:
        objects: A (nested) collection of objects.  They are placed
          onto the canvas in order after flattening.
        w: Width of the canvas.
        h: Height of the canvas.
        t: If objects are dynamic, the timepoint to render.

    """
    defs = []
    filters = []
    out = '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" '
    out += 'xmlns:xlink="http://www.w3.org/1999/xlink" '
    out += 'width="{}" height="{}">\n'.format(w, h)

    # # flip y-axis so zero is at the bottom:
    # scale_shapes(objects, 1, -1)
    # translate_shapes(objects, 0, h)

    objects = "".join(
        [_write_shape(obj, defs, filters, t) for obj in flatten(objects)]
    )

    defs.extend(_write_filters(filters))
    out += "<defs>\n" + "".join(defs) + "</defs>\n"

    out += '<g transform="translate(0, {}) scale(1, -1)">\n'.format(h)
    out += objects + "</g>\n</svg>\n"
    return out


def gif(
    function: Callable,
    fps: int,
    file_name: str,
    n_frames: int = None,
    seconds: float = None,
):
    """Create a GIF image from a frame-generating function.

    By wrapping typical canvas drawing code in a function, multiple
    versions of the drawing, each with random variation, can be
    stitched together into an animated GIF.

    Args:
        function: A function called with no arguments that returns a
          (filled) Canvas.
        fps: Frames per second of the GIF.
        file_name: The file name to write to.
        n_frames: Number of frames to generate.
        seconds: Specify length of the GIF in seconds instead of
          number of frames.

    """
    if n_frames is None:
        n_frames = seconds * fps
    files = _write_frames(function, n_frames, fps)
    ImageSequenceClip(files, fps=fps).write_gif(file_name, logger=None)


def video(
    function: Callable,
    fps: int,
    file_name: str,
    n_frames: int = None,
    seconds: float = None,
):
    """Create a GIF image from a frame-generating function.

    By wrapping typical canvas drawing code in a function, multiple
    versions of the drawing, each with random variation, can be
    stitched together into an animated GIF.

    Args:
        function: A function called with no arguments that returns a
          (filled) Canvas.
        fps: Frames per second of the GIF.
        file_name: The file name to write to.
        n_frames: Number of frames to generate.
        seconds: Specify length of the GIF in seconds instead of
          number of frames.

    """
    if n_frames is None:
        n_frames = seconds * fps
    files = _write_frames(function, n_frames, fps)
    ImageSequenceClip(files, fps=fps).write_videofile(file_name, logger=None)
