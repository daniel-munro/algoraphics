"""
wrapping_paper.py
=================
Fill a space with non-overlapping copies of doodles.

"""

import math
import numpy as np
import random

from .main import rotate_shapes, translate_shapes, scale_shapes, bounding_box
from .main import rotated_bounding_box, keep_shapes_inside


class Doodle:
    def __init__(self, function, footprint):
        """Row 0 of the footprint should correspond to the top row of the doodle's footprint."""
        self.function = function
        # Reverse footprint so that row 0 is the bottom.
        self.fp = np.array(footprint[::-1])
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

    Argps:
        outline (dict|list): A shape or (nested) list of shapes that will become the clip.
        spacing (float): Height/width of each grid cell.
        doodles (list): A list of Doodle objects.
        rotate (bool): Whether to place the grid in a random rotated orientation.

    Returns:
        dict: A clipped group.

    """
    if rotate:
        rotation = random.uniform(0, 90)
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
