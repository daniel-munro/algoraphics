"""
fill.py
================
Fill regions with objects in various ways.

"""

import math
import numpy as np
from typing import Union, Callable, Tuple, List, Sequence

from .main import add_margin, flatten
from .shapes import (
    bounding_box,
    coverage,
    remove_hidden,
    keep_points_inside,
    rotated_bounding_box,
    keep_shapes_inside,
    circle,
    rotate_shapes,
    translate_shapes,
    scale_shapes,
    sample_points_in_shape,
    set_style,
)
from .geom import distance, rand_point_on_circle, deg, spaced_points
from .structures import filament
from .param import Param, make_param, fixed_value
from .color import Color, make_color

Number = Union[int, float]
Point = Tuple[Number, Number]
Bounds = Tuple[Number, Number, Number, Number]
Collection = Union[dict, list]


def fill_region(
    outline: Collection,
    object_fun: Callable[[Bounds], Collection],
    max_tries: int = None,
) -> dict:
    """Fill a region by iteratively placing randomly generated objects.

    Args:
        outline: A shape or (nested) list of shapes that will become clip.
        object_fun: A function that takes bounds as input and returns
          one randomly generated object.  Usually this is a lambda
          function that calls another function using arguments passed
          to the function that produced the lambda function.  i.e.,
          def caller_fun(args...): return lambda bounds:
          helper_fun(bounds, args...)
        max_tries: If not None, the number of objects to generate
          (including those discarded for not filling space) before
          giving up and returning the region as is.

    Returns:
        A group with clip.

    """
    bounds = add_margin(bounding_box(outline), 10)
    space = coverage(outline)
    objects = []
    try_count = 0
    while space.area > 0.1 and (max_tries is None or try_count < max_tries):
        try_count += 1
        obj = object_fun(bounds)
        # space_copy = copy.deepcopy(space)
        old_area = space.area
        shapes = [coverage(o) for o in flatten(obj)]
        for shape in shapes:
            space = space.difference(shape)
        if space.area < old_area:
            objects.append(obj)
            # space = space_copy

    filled_region = dict(type="group", clip=outline, members=objects)
    remove_hidden(filled_region)
    return filled_region


def _filament_fill_obj(
    bounds: Bounds,
    direction_delta: Param,
    width: Param,
    seg_length: Param,
    color: Color,
) -> List[dict]:
    """Generate filament extending into bounds.

    Called indirectly by lambda function produced by filament_fill().

    Args:
        bounds: A bounds tuple.
        direction_delta: Parameter that will become the delta for the
          filament direction.
        width: Width of the filament.
        seg_length: Average side length of each segment.
        color: Color specification for filament segments.  A separate
          copy is used for each filament in case it involves
          deltas/ratios.

    Returns:
        The ordered segment polygons.

    """
    direction_delta = make_param(direction_delta)
    width = make_param(width)
    seg_length = make_param(seg_length)
    color = make_color(color)

    c = ((bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2)
    r = distance(c, (bounds[2], bounds[3]))
    start = rand_point_on_circle(c, r)
    angle = math.atan2(c[1] - start[1], c[0] - start[0])
    dir_start = deg(angle) + np.random.uniform(-60, 60)
    direction = Param(dir_start, delta=direction_delta)
    n_segments = int(2.2 * r / seg_length.mean)
    x = filament(start, direction, width, seg_length, n_segments)
    set_style(x, "fill", color)
    return x


def filament_fill(
    direction_delta: Param, width: Number, seg_length: Number, color: Color
) -> Callable[[Bounds], List[dict]]:
    """Generate filament fill function.

    Args:
        direction_delta: Parameter that will become the delta for the
          filament direction.
        width: Width of the filament.
        seg_length: Average side length of each segment.
        color: Color specification for filament segments.  A separate
          copy is used for each filament in case it involves
          deltas/ratios.

    Returns:
        A function used by fill_region().

    """
    return lambda bounds: _filament_fill_obj(
        bounds, direction_delta, width, seg_length, color
    )


class Doodle:
    """A Doodle object is a generator of doodles.

    Args:
        function: A function that takes no arguments and returns a
          shape or collection.
        footprint: A boolean 2D array whose cells indicate the shape
          (within a grid) occupied by the generated doodles (before
          being oriented).  Row 0 should correspond to the top row of
          the doodle's footprint.

    """

    def __init__(self, function: Callable[[], Collection], footprint: np.ndarray):
        self.function = function
        # Reverse footprint so that row 0 is the bottom.
        self.fp = np.array(footprint)[::-1]
        self.n_cells = np.sum(self.fp)
        self.orientations = np.array([True] * 8)

    def footprint(self, orientation: int = 0) -> np.ndarray:
        """Get the doodle's footprint in a given orientation.

        Args:
           orientation: 0 to 7.

        Returns:
            The oriented footprint.

        """
        # Rotate in the same direction as the shapes:
        oriented = np.rot90(self.fp, -(orientation % 4))
        if orientation > 3:
            oriented = oriented.transpose()
        return oriented

    def oriented(self, orientation: int = 0) -> Collection:
        """Draw the doodle in a given orientation.

        Args:
            orientation: 0 to 7.

        Returns:
            The oriented doodle.

        """
        dim = self.fp.shape
        x = self.function()
        assert orientation in range(8)
        rotate = orientation % 4
        rotate_shapes(x, rotate * 90)
        if rotate == 1:
            translate_shapes(x, dim[0], 0)
        elif rotate == 2:
            translate_shapes(x, dim[1], dim[0])
        elif rotate == 3:
            translate_shapes(x, 0, dim[1])
        if orientation > 3:
            scale_shapes(x, 1, -1)
            rotate_shapes(x, 90)
        return x


def _doodle_fits(grid: np.ndarray, coords: Point, footprint: np.ndarray) -> bool:
    """Determine whether a doodle will fit at a location.

    Args:
        grid: A boolean array of occupied locations.
        coords: The top left corner of the location to test.
        footprint: The doodle's oriented footprint.

    Returns:
        Whether the space is available for the footprint.

    """
    subgrid = grid[
        coords[0] : (coords[0] + footprint.shape[0]),
        coords[1] : (coords[1] + footprint.shape[1]),
    ]
    return np.sum(np.logical_and(subgrid, footprint)) == 0


def _add_doodle(grid: np.ndarray, coords: Point, footprint: np.ndarray):
    """Mark the space where a doodle is placed as occupied.

    Args:
        grid: A boolean array of occupied locations.
        coords: The top left corner of the new doodle's location.
        footprint: The doodle's footprint.

    """
    subgrid = grid[
        coords[0] : (coords[0] + footprint.shape[0]),
        coords[1] : (coords[1] + footprint.shape[1]),
    ]
    grid[
        coords[0] : (coords[0] + footprint.shape[0]),
        coords[1] : (coords[1] + footprint.shape[1]),
    ] = np.logical_or(subgrid, footprint)


def _next_cell(r, c, rows, cols):
    """Get the next cell for iterating through the grid."""
    c += 1
    if c == cols:
        c = 0
        r += 1
        if r == rows:
            r = 0
    return (r, c)


def grid_wrapping_paper(
    rows: int, cols: int, spacing: Number, start: Point, doodles: Sequence[Doodle]
) -> List[Collection]:
    """Create a tiling of non-overlapping doodles.

    Args:
        rows: Number of rows to include.
        cols: Number of columns to include.
        spacing: Height/width of each grid cell.
        start: Bottom left point of the grid.
        doodles: A list of Doodle objects.

    Returns:
        A list of placed doodle collections.

        """
    # Margin = extra cells to allow tiling to fill the desired grid.
    margin = max([max(doodle.footprint().shape) for doodle in doodles]) - 1
    occupied = np.zeros((rows + 2 * margin, cols + 2 * margin), dtype=bool)
    shapes = []

    while np.sum(np.logical_not(occupied)) > 0 and len(doodles) > 0:
        # Choose from remaining doodles weighted by size.
        n_cells = [doodle.n_cells for doodle in doodles]
        weights = [x / float(sum(n_cells)) for x in n_cells]
        o = np.random.choice(range(len(doodles)), p=weights)
        doodle = doodles[o]

        # Get footprint of randomly rotated/flipped doodle.
        orientation = np.random.choice(np.where(doodle.orientations)[0])
        oriented = doodle.footprint(orientation)

        # Move through grid to find open space for object.
        r_start = np.random.choice(range(margin + rows))
        c_start = np.random.choice(range(margin + cols))
        (r, c) = (r_start, c_start)
        while True:
            # If oriented doodle can be placed somewhere, place it.
            if _doodle_fits(occupied, (r, c), oriented):
                _add_doodle(occupied, (r, c), oriented)
                shape = doodle.oriented(orientation)
                translate_shapes(shape, c, r)
                shapes.append(shape)
                break

            (r, c) = _next_cell(r, c, margin + rows, margin + cols)
            # If it couldn't be placed anywhere, check off that orientation.
            if (r, c) == (r_start, c_start):
                doodle.orientations[orientation] = False
                if not np.any(doodle.orientations):
                    del doodles[o]
                break

    translate_shapes(shapes, -margin, -margin)
    scale_shapes(shapes, spacing)
    translate_shapes(shapes, start[0], start[1])
    return shapes


def fill_wrapping_paper(
    outline: Collection, spacing: Number, doodles: Sequence[Doodle], rotate: bool = True
) -> dict:
    """Fill a region with a tiling of non-overlapping doodles.

    Args:
        outline: A shape or (nested) list of shapes that will become the clip.
        spacing: Height/width of each grid cell.
        doodles: A list of Doodle objects.
        rotate: Whether to place the grid in a random rotated orientation.

    Returns:
        A clipped group.

    """
    if rotate:
        rotation = np.random.uniform(0, 90)
        bounds = rotated_bounding_box(outline, rotation)
    else:
        bounds = bounding_box(outline)

    rows = int(math.ceil((bounds[3] - bounds[1]) / spacing))
    cols = int(math.ceil((bounds[2] - bounds[0]) / spacing))
    fill = grid_wrapping_paper(rows, cols, spacing, (bounds[0], bounds[1]), doodles)

    if rotate:
        rotate_shapes(fill, rotation)
    keep_shapes_inside(fill, outline)

    return dict(type="group", clip=outline, members=[fill])


def fill_spots(
    outline: Collection, spacing: Number = 10, radius: Param = None
) -> List[dict]:
    """Fill a region with randomly sized spots.

    The spots are reminiscent of Ishihara color blindness tests.  The
    spots are not completely non-overlapping, but overlaps are
    somewhat avoided by spacing out their centers.

    Args:
        outline: A region outline shape.
        spacing: The approximate distance between the centers of
          neighboring spots.
        radius: The spot radius.  By default the radii range from
          ``spacing`` to ``spacing`` / 5 in a geometric sequence.  If
          provided, it is recommended to supply a parameter with ratio
          < 1 so that spaced-out larger points are plotted first, with
          progressively smaller points inserted between existing ones.

    Returns:
        A list of circle shapes.

    """
    spacing = fixed_value(spacing)
    bounds = bounding_box(outline)
    bounds_area = (bounds[2] - bounds[0]) * (bounds[3] - bounds[1])
    n_points = int(bounds_area / spacing ** 2) + 1
    points = spaced_points(n_points, bounds, n_cand=10)
    keep_points_inside(points, outline)
    if len(points) == 0:
        points = sample_points_in_shape(outline, 1)
    if radius is None:
        ratio = ((spacing / 5) / spacing) ** (1 / (len(points) - 1))
        radius = Param(spacing, ratio=ratio)
    else:
        radius = make_param(radius)
    return [circle(c=points[i], r=radius.value()) for i in range(len(points))]
