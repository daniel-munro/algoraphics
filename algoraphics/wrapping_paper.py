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


def object_fits(grid, coords, footprint):
    subgrid = grid[coords[0]:(coords[0] + footprint.shape[0]),
                   coords[1]:(coords[1] + footprint.shape[1])]
    return np.sum(np.logical_and(subgrid, footprint)) == 0


def add_object(grid, coords, footprint):
    subgrid = grid[coords[0]:(coords[0] + footprint.shape[0]),
                   coords[1]:(coords[1] + footprint.shape[1])]
    grid[coords[0]:(coords[0] + footprint.shape[0]),
         coords[1]:(coords[1] + footprint.shape[1])] = np.logical_or(subgrid,
                                                                     footprint)


def next_cell(r, c, rows, cols):
    c += 1
    if c == cols:
        c = 0
        r += 1
        if r == rows:
            r = 0
    return (r, c)


def oriented_doodle(fun, rotate, flip):
    dim = fun(footprint=True).shape
    x = fun()
    rotate_shapes(x, rotate * 90)
    if rotate == 1:
        translate_shapes(x, dim[0], 0)
    elif rotate == 2:
        translate_shapes(x, dim[1], dim[0])
    elif rotate == 3:
        translate_shapes(x, 0, dim[1])
    if flip:
        scale_shapes(x, 1, -1)
        rotate_shapes(x, 90)
    return x


def grid_wrapping_paper(rows, cols, spacing, start, doodles):
    margin = max([max(doodle(footprint=True).shape) for doodle in doodles]) - 1
    occupied = np.zeros((rows + 2 * margin, cols + 2 * margin), dtype=bool)
    objects = [dict(fun=doodle,
                    n_cells=np.sum(doodle(footprint=True)),
                    orientations=np.array([True] * 8)) for doodle in doodles]
    shapes = []

    while(np.sum(np.logical_not(occupied)) > 0 and len(objects) > 0):
        # choose from remaining objects weighted by size
        n_cells = [x['n_cells'] for x in objects]
        weights = [x / float(sum(n_cells)) for x in n_cells]
        o = np.random.choice(range(len(objects)), p=weights)
        obj = objects[o]

        # get footprint of randomly rotated/flipped object
        orientation = np.random.choice(np.where(obj['orientations'])[0])
        oriented = np.rot90(obj['fun'](footprint=True), -(orientation % 4))
        if orientation > 3:
            oriented = oriented.transpose()

        # move through grid to find open space for object
        r_start = random.randrange(margin + rows)
        c_start = random.randrange(margin + cols)
        (r, c) = (r_start, c_start)
        while True:
            if object_fits(occupied, (r, c), oriented):
                add_object(occupied, (r, c), oriented)
                shape = oriented_doodle(obj['fun'],
                                        rotate=orientation % 4,
                                        flip=orientation > 3)
                translate_shapes(shape, c, r)
                shapes.append(shape)
                break

            (r, c) = next_cell(r, c, margin + rows, margin + cols)
            if (r, c) == (r_start, c_start):
                obj['orientations'][orientation] = False
                if not np.any(obj['orientations']):
                    del objects[o]
                break

    translate_shapes(shapes, -margin, -margin)
    scale_shapes(shapes, spacing)
    translate_shapes(shapes, start[0], start[1])
    return shapes


def fill_wrapping_paper(outline, spacing, doodles, rotate=True):
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
