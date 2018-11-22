"""
fill.py
================
Fill regions with objects in various ways.

"""

import math
import numpy as np

from .main import set_style, add_margin, flatten
from .shapes import bounding_box, coverage, remove_hidden, keep_points_inside
from .shapes import rotated_bounding_box, keep_shapes_inside, circle
from .shapes import rotate_shapes, translate_shapes, scale_shapes
from .shapes import sample_points_in_shape
from .geom import distance, rand_point_on_circle, deg
from .structures import filament
from .tiling import mitchell_points
from .param import Param, make_param, fixed_value
from .color import make_color


def fill_region(outline, object_fun, max_tries=None):
    """Fill a region by iteratively placing randomly generated objects.

    Args:
        outline (dict|list): A shape or (nested) list of shapes that will become clip.
        object_fun (function): A function that takes bounds as input and returns one randomly generated object.  Usually this is a lambda function that calls another function using arguments passed to the function that produced the lambda function.  i.e., def caller_fun(args...): return lambda bounds: helper_fun(bounds, args...)
        max_tries (int): If not None, the number of objects to generate (including those discarded for not filling space) before giving up and returning the region as is.

    Returns:
        dict: A group with clip.

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

    filled_region = dict(type='group', clip=outline, members=objects)
    remove_hidden(filled_region)
    return filled_region


def _filament_fill_obj(bounds, direction_delta, width, seg_length, color):
    """Generate filament extending into bounds.

    Called indirectly by lambda function produced by filament_fill().

    Args:
        bounds (tuple): A bounds tuple.
        direction_delta (Param): Parameter that will become the delta for the filament direction.
        width (float|int): Width of the filament.
        seg_length (float|int): Average side length of each segment.
        color (Color): Color specification for filament segments.  A separate copy is used for each filament in case it involves deltas/ratios.

    Returns:
        list: The ordered segment polygons.

    """
    direction_delta = make_param(direction_delta)
    width = make_param(width)
    seg_length = make_param(seg_length)
    color = make_color(color)

    c = ((bounds[0] + bounds[1]) / 2., (bounds[2] + bounds[3]) / 2.)
    r = distance(c, (bounds[1], bounds[3]))
    start = rand_point_on_circle(c, r)
    angle = math.atan2(c[1] - start[1], c[0] - start[0])
    dir_start = deg(angle) + np.random.uniform(-60, 60)
    direction = Param(dir_start, delta=direction_delta)
    n_segments = int(2.2 * r / seg_length.mean)
    x = filament(start, direction, width, seg_length, n_segments)
    set_style(x, 'fill', color)
    return x


def filament_fill(direction_delta, width, seg_length, color):
    """Generate filament fill function.

    Args:
        direction_delta (Param): Parameter that will become the delta for the filament direction.
        width (float|int): Width of the filament.
        seg_length (float|int): Average side length of each segment.
        color (Color): Color specification for filament segments.  A separate copy is used for each filament in case it involves deltas/ratios.

    Returns:
        function: A function used by fill_region().

    """
    return lambda bounds: _filament_fill_obj(bounds, direction_delta,
                                             width, seg_length, color)


class Doodle:
    def __init__(self, function, footprint):
        """Row 0 of the footprint should correspond to the top row of the doodle's footprint."""
        self.function = function
        # Reverse footprint so that row 0 is the bottom.
        self.fp = np.array(footprint)[::-1]
        self.n_cells = np.sum(self.fp)
        self.orientations = np.array([True] * 8)

    def footprint(self, orientation=0):
        """Get the doodle's footprint in a given orientation.

        Args:
           orientation (int): 0 to 7.

        Returns:
            numpy.ndarray: The oriented footprint.

        """
        # Rotate in the same direction as the shapes:
        oriented = np.rot90(self.fp, -(orientation % 4))
        if orientation > 3:
            oriented = oriented.transpose()
        return oriented

    def oriented(self, orientation=0):
        """Draw the doodle in a given orientation.

        Args:
            orientation (int): 0 to 7.

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


def _doodle_fits(grid, coords, footprint):
    """Determine whether a doodle will fit at a location.

    Args:
        grid (numpy.ndarray): A boolean array of occupied locations.
        coords (tuple): The top left corner of the location to test.
        footprint (numpy.ndarray): The doodle's oriented footprint.

    Returns:
        bool: Whether the space is available for the footprint.

    """
    subgrid = grid[coords[0]:(coords[0] + footprint.shape[0]),
                   coords[1]:(coords[1] + footprint.shape[1])]
    return np.sum(np.logical_and(subgrid, footprint)) == 0


def _add_doodle(grid, coords, footprint):
    """Mark the space where a doodle is placed as occupied.

    Args:
        grid (numpy.ndarray): A boolean array of occupied locations.
        coords (tuple): The top left corner of the new doodle's location.
        footprint (numpy.ndarray): The doodle's footprint.

    """
    subgrid = grid[coords[0]:(coords[0] + footprint.shape[0]),
                   coords[1]:(coords[1] + footprint.shape[1])]
    grid[coords[0]:(coords[0] + footprint.shape[0]),
         coords[1]:(coords[1] + footprint.shape[1])] = np.logical_or(subgrid,
                                                                     footprint)


def _next_cell(r, c, rows, cols):
    """Get next cell for iterating through the grid."""
    c += 1
    if c == cols:
        c = 0
        r += 1
        if r == rows:
            r = 0
    return (r, c)


def grid_wrapping_paper(rows, cols, spacing, start, doodles):
    """Create a tiling of non-overlapping doodles.

    Args:
        rows (int): Number of rows to include.
        cols (int): Number of columns to include.
        spacing (float): Height/width of each grid cell.
        start (tuple): Bottom left point of the grid.
        doodles (list): A list of doodle functions.

    Returns:
        list: A list of placed doodle objects.

        """
    # Margin = extra cells to allow tiling to fill the desired grid.
    margin = max([max(doodle.footprint().shape) for doodle in doodles]) - 1
    occupied = np.zeros((rows + 2 * margin, cols + 2 * margin), dtype=bool)
    shapes = []

    while(np.sum(np.logical_not(occupied)) > 0 and len(doodles) > 0):
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


def fill_wrapping_paper(outline, spacing, doodles, rotate=True):
    """Fill a region with a tiling of non-overlapping doodles.

    Args:
        outline (dict|list): A shape or (nested) list of shapes that will become the clip.
        spacing (float): Height/width of each grid cell.
        doodles (list): A list of Doodle objects.
        rotate (bool): Whether to place the grid in a random rotated orientation.

    Returns:
        dict: A clipped group.

    """
    if rotate:
        rotation = np.random.uniform(0, 90)
        bounds = rotated_bounding_box(outline, rotation)
    else:
        bounds = bounding_box(outline)

    rows = int(math.ceil((bounds[3] - bounds[2]) / float(spacing)))
    cols = int(math.ceil((bounds[1] - bounds[0]) / float(spacing)))
    fill = grid_wrapping_paper(rows, cols, spacing, (bounds[0], bounds[2]),
                               doodles)

    if rotate:
        rotate_shapes(fill, rotation)
    # Doesn't work on paths (needs list of points):
    keep_shapes_inside(fill, outline)

    return dict(type='group', clip=outline, members=[fill])


def fill_ishihara_spots(outline, spacing=10, radius=None):
    """Fill a region with randomly sized spots.

    The spots are reminiscent of Ishihara color blindness tests.
    The spots are not completely non-overlapping, but overlaps are
    somewhat avoided by spacing out their centers.

    Args:
        outline (dict|list): A region outline shape.
        spacing (float): The approximate distance between the centers of neighboring spots.
        radius (Param): The spot radius.  By default the radii range from `spacing` to `spacing` / 5 in a geometric sequence.  If provided, it is recommended to supply a parameter with ratio < 1 so that spaced-out larger points are plotted first, with progressively smaller points inserted between existing ones.

    Returns:
        list: A list of circle shapes.

    """
    spacing = fixed_value(spacing)
    # radius2 = make_param(radius)
    # sample = [radius2.value() for i in range(100)]
    # r_mean = np.mean(sample)
    bounds = bounding_box(outline)
    bounds_area = (bounds[1] - bounds[0]) * (bounds[3] - bounds[2])
    # n_points = int(bounds_area / (3.14 * r_mean ** 2)) + 1
    n_points = int(bounds_area / spacing ** 2) + 1
    points = mitchell_points(n_points, 10, bounds)
    keep_points_inside(points, outline)
    if len(points) == 0:
        points = sample_points_in_shape(outline, 1)
    if radius is None:
        ratio = ((spacing / 5) / spacing) ** (1. / (len(points) - 1))
        radius = Param(spacing, ratio=ratio)
    else:
        radius = make_param(radius)
    return [circle(c=points[i], r=radius.value()) for i in
            range(len(points))]
