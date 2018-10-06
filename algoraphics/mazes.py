"""
mazes.py
========
Create maze-like fill patterns.

"""

import math
import random
import copy

from .main import rotate_path, translate_path, scale_path, bounding_box
from .main import rotated_bounding_box, add_margin, rotate_shapes, set_style
from .grid import grid_tree_neighbors
from .color import rgb_to_hsl


def rotated_piece(path, times):
    path = copy.deepcopy(path)
    rotate_cell(path, times)
    return path


class Maze_Style_Pipes:
    """Generate pieces for curved pipes.

    Args:
        rel_thickness (float): Channel width relative to cell width, from 0 to 1.

    """
    def __init__(self, rel_thickness):
        self.rel_thickness = rel_thickness

    def draw(self, shape):
        w = self.rel_thickness / 2.
        r_in = (0.5 - w) * self.rel_thickness  # inner curve radius
        p1 = (0.5 + w, 0.5 - w - r_in)  # beginning of inner curve
        p2 = (0.5 + w + r_in, 0.5 - w)  # end of inner curve
        right_turn = [dict(command='L', to=p1)]
        right_turn.append(dict(command='A', r=r_in, large_arc=False,
                               positive=False, to=p2))

        if shape == 'tip':
            path = [dict(command='L', to=(0.5 + w, 0.5))]
            path.append(dict(command='A', r=w, large_arc=False, positive=True,
                             to=(0.5 - w, 0.5)))
            return path

        elif shape == 'turn':
            path1 = right_turn
            path2 = [dict(command='L', to=(0.5, 0.5 + w))]
            path2.append(dict(command='A', r=w, large_arc=False, positive=True,
                              to=(0.5 - w, 0.5)))
            return (path1, path2)

        elif shape == 'straight':
            return ([], [])

        elif shape == 'T':
            path1 = right_turn
            path2 = rotated_piece(right_turn, 3)
            return (path1, [], path2)

        elif shape == 'cross':
            path1 = right_turn
            path2 = rotated_piece(right_turn, 1)
            path3 = rotated_piece(right_turn, 2)
            path4 = rotated_piece(right_turn, 3)
            return (path1, path2, path3, path4)


class Maze_Style_Round:
    """Generate pieces for very curvy pipes.

    Args:
        rel_thickness (float): Channel width relative to cell width, from 0 to 1.

    """
    def __init__(self, rel_thickness):
        self.rel_thickness = rel_thickness

    def draw(self, shape):
        w = self.rel_thickness / 2.
        right_turn = [dict(command='A', r=0.5 - w, large_arc=False,
                           positive=False, to=(1, 0.5 - w))]

        if shape == 'tip':
            path = [dict(command='L', to=(0.5 + w, 0.5))]
            path.append(dict(command='A', r=w, large_arc=False, positive=True,
                             to=(0.5 - w, 0.5)))
            path.append(dict(command='L', to=(0.5 - w, 0)))
            return path

        elif shape == 'turn':
            path1 = right_turn
            path2 = [dict(command='A', r=0.5 + w, large_arc=False,
                          positive=True, to=(0.5 - w, 0))]
            return (path1, path2)

        elif shape == 'straight':
            path1 = [dict(command='L', to=(0.5 + w, 1))]
            path2 = [dict(command='L', to=(0.5 - w, 0))]
            return (path1, path2)

        elif shape == 'T':
            path1 = right_turn
            p = (0.5, math.sqrt((0.5 + w) ** 2 - 0.5 ** 2))
            path2 = [dict(command='A', r=0.5 + w, large_arc=False,
                          positive=True, to=p)]
            path2.append(dict(command='A', r=0.5 + w, large_arc=False,
                              positive=True, to=(0, 0.5 + w)))
            path3 = rotated_piece(right_turn, 3)
            return (path1, path2, path3)

        elif shape == 'cross':
            # path1 = right_turn
            # path2 = rotated_piece(right_turn, 1)
            # path3 = rotated_piece(right_turn, 2)
            # path4 = rotated_piece(right_turn, 3)
            path1 = [dict(command='L', to=(0.5 + w, 0.5 - w))]
            path1.append(dict(command='L', to=(1, 0.5 - w)))
            path2 = rotated_piece(path1, 1)
            path3 = rotated_piece(path1, 2)
            path4 = rotated_piece(path1, 3)
            return (path1, path2, path3, path4)


class Maze_Style_Straight:
    """Generate pieces for simple right-angle maze.

    Args:
        rel_thickness (float): Channel width relative to cell width, from 0 to 1.

    """
    def __init__(self, rel_thickness):
        self.rel_thickness = rel_thickness

    def draw(self, shape):
        def move_to(x, y):
            return dict(command='L', to=(x, y))
        w = self.rel_thickness / 2.

        if shape == 'tip':
            path = [move_to(0.5 + w, 0.5 + w)]
            path.append(move_to(0.5 - w, 0.5 + w))
            return path

        elif shape == 'turn':
            path1 = [move_to(0.5 + w, 0.5 - w)]
            path2 = [move_to(0.5 - w, 0.5 + w)]
            return (path1, path2)

        elif shape == 'straight':
            return ([], [])

        elif shape == 'T':
            path1 = [move_to(0.5 + w, 0.5 - w)]
            path2 = [move_to(0.5 - w, 0.5 - w)]
            return (path1, [], path2)

        elif shape == 'cross':
            path1 = [move_to(0.5 + w, 0.5 - w)]
            path2 = [move_to(0.5 + w, 0.5 + w)]
            path3 = [move_to(0.5 - w, 0.5 + w)]
            path4 = [move_to(0.5 - w, 0.5 - w)]
            return (path1, path2, path3, path4)


class Maze_Style_Jagged:
    """Generate pieces for jagged maze.

    Args:
        min_w (float): Minimum width of channel segment relative to cell width.
        max_w (float): Maximum width of channel segment relative to cell width.

    """

    def __init__(self, min_w, max_w):
        self.min_w = min_w
        self.max_w = max_w

    def draw(self, shape):
        def move_to(x, y):
            return dict(command='L', to=(x, y))

        def dev():
            return random.uniform(self.min_w / 2., self.max_w / 2.)

        def big_dev():
            return random.uniform(-self.max_w / 2., self.max_w / 2.)

        if shape == 'tip':
            path = [move_to(0.5 + dev(), 0.5 + dev())]
            path.append(move_to(0.5 - dev(), 0.5 + dev()))
            return path

        elif shape == 'turn':
            path1 = [move_to(0.5 + dev(), 0.5 - dev())]
            path2 = [move_to(0.5 - dev(), 0.5 + dev())]
            return (path1, path2)

        elif shape == 'straight':
            path1 = [move_to(0.5 + dev(), 0.5 + big_dev())]
            path2 = [move_to(0.5 - dev(), 0.5 + big_dev())]
            return (path1, path2)

        elif shape == 'T':
            path1 = [move_to(0.5 + dev(), 0.5 - dev())]
            path2 = [move_to(0.5 + big_dev(), 0.5 + dev())]
            path3 = [move_to(0.5 - dev(), 0.5 - dev())]
            return (path1, path2, path3)

        elif shape == 'cross':
            path1 = [move_to(0.5 + dev(), 0.5 - dev())]
            path2 = [move_to(0.5 + dev(), 0.5 + dev())]
            path3 = [move_to(0.5 - dev(), 0.5 + dev())]
            path4 = [move_to(0.5 - dev(), 0.5 - dev())]
            return (path1, path2, path3, path4)


def new_coords(prev_coords, direction):
    """Get grid coordinates after moving one step from `prev_coords` in `direction`.

    Args:
        prev_coords (tuple): The starting (r, c) coordinates.
        direction (int): Direction of movement (0=d, 1=r, 2=u, 3=l).

    Returns:
        The new grid coordinate tuple.

    """
    r, c = prev_coords
    if direction == 0:
        r -= 1
    elif direction == 1:
        c += 1
    elif direction == 2:
        r += 1
    elif direction == 3:
        c -= 1
    return (r, c)


def rotate_cell(path, times):
    """Rotate path/s at right angles within grid cell.

    Args:
        path (list|tuple): A path list or tuple of path lists.
        times (int): Number of 90 degree counter-clockwise turns.

    """
    times = times % 4
    if isinstance(path, tuple):  # multiple paths
        for p in path:
            rotate_cell(p, times)
    elif times > 0:
        rotate_path(path, times * 90, (0.5, 0.5))


def translate_cell(path, coords):
    """Translate path/s to grid coordinate.

    Treats grid cells as having width 1.

    Args:
        path (list, tuple): A path list or tuple of path lists.
        coords (tuple): The (r, c) coordinates to move to.

    """
    if isinstance(path, tuple):  # multiple paths
        for p in path:
            translate_cell(p, coords)
    else:
        translate_path(path, coords[1], coords[0])


def process_neighbor(coords, direc, neighbor_mat, style):
    """Call draw_cell() on neighboring cell.

    Args:
        coords (tuple): The current (r, c) coordinates.
        direc (int): Direction of neighbor to process (0=d, 1=r, 2=u, 3=l).
        neighbor_mat (numpy.ndarray): A boolean array with dimensions (rows, cols, 4) indicating if neighboring cells are connected.
        draw_fun (function): A drawing function.

    Returns:
        Path list for neighboring subtree.

    """
    coords2 = new_coords(coords, direc % 4)
    return draw_cell(coords2, (direc + 2) % 4, neighbor_mat, style)


def draw_cell(coords, dir_from, neighbor_mat, style):
    """Get subtree path recursively for a cell.

    Args:
        coords (tuple): The current (r, c) coordinates.
        dir_from (int): Direction from which cell was entered (returned subtree will include the remaining connected directions).
        neighbor_mat (numpy.ndarray): boolean array with dimensions (rows, cols, 4) indicating if neighboring cells are connected.
        draw_fun (function): A drawing function.

    Returns:
        Path list for subtree that excludes everything in the
        originating direction.

    """
    neighbors = neighbor_mat[coords]
    r = neighbors[(dir_from + 1) % 4]
    s = neighbors[(dir_from + 2) % 4]
    le = neighbors[(dir_from + 3) % 4]

    # U-turn:
    if not r and not s and not le:
        path = style.draw('tip')
        rotate_cell(path, dir_from)
        translate_cell(path, coords)

    # right turn:
    elif r and not s and not le:
        paths = style.draw('turn')
        rotate_cell(paths, dir_from)
        translate_cell(paths, coords)
        n = process_neighbor(coords, dir_from + 1, neighbor_mat, style)
        path = paths[0] + n + paths[1]

    # left turn:
    elif not r and not s and le:
        paths = style.draw('turn')
        rotate_cell(paths, dir_from + 3)
        translate_cell(paths, coords)
        n = process_neighbor(coords, dir_from + 3, neighbor_mat, style)
        path = paths[1] + n + paths[0]

    # straight:
    elif not r and s and not le:
        paths = style.draw('straight')
        rotate_cell(paths, dir_from)
        translate_cell(paths, coords)
        n = process_neighbor(coords, dir_from + 2, neighbor_mat, style)
        path = paths[0] + n + paths[1]

    # T:
    elif r and not s and le:
        paths = style.draw('T')
        rotate_cell(paths, dir_from)
        translate_cell(paths, coords)
        n1 = process_neighbor(coords, dir_from + 1, neighbor_mat, style)
        n2 = process_neighbor(coords, dir_from + 3, neighbor_mat, style)
        path = paths[0] + n1 + paths[1] + n2 + paths[2]

    elif r and s and not le:
        paths = style.draw('T')
        rotate_cell(paths, dir_from + 1)
        translate_cell(paths, coords)
        n1 = process_neighbor(coords, dir_from + 1, neighbor_mat, style)
        n2 = process_neighbor(coords, dir_from + 2, neighbor_mat, style)
        path = paths[2] + n1 + paths[0] + n2 + paths[1]

    elif not r and s and le:
        paths = style.draw('T')
        rotate_cell(paths, dir_from + 3)
        translate_cell(paths, coords)
        n1 = process_neighbor(coords, dir_from + 2, neighbor_mat, style)
        n2 = process_neighbor(coords, dir_from + 3, neighbor_mat, style)
        path = paths[1] + n1 + paths[2] + n2 + paths[0]

    # cross:
    elif r and s and le:
        paths = style.draw('cross')
        rotate_cell(paths, dir_from)
        translate_cell(paths, coords)
        n1 = process_neighbor(coords, dir_from + 1, neighbor_mat, style)
        n2 = process_neighbor(coords, dir_from + 2, neighbor_mat, style)
        n3 = process_neighbor(coords, dir_from + 3, neighbor_mat, style)
        path = paths[0] + n1 + paths[1] + n2 + paths[2] + n3 + paths[3]

    return path


def maze(rows, cols, spacing, start, style):
    """Generate a maze-like pattern spanning the specified grid.

    Args:
        rows (int): Number of rows in grid.
        cols (int): Number of cols in grid.
        spacing (number): The cell width.
        start (point): The bottom-left coordinate of the grid.
        draw_fun (function): A maze-drawing function that takes a component keyword and returns one or more paths to be assembled.

    Returns:
        A path shape.

    """
    neighbor_mat = grid_tree_neighbors(rows, cols)
    r = neighbor_mat[0, 0, 1]
    u = neighbor_mat[0, 0, 2]

    if r and not u:
        path = style.draw('tip')
        rotate_cell(path, 1)
        path += process_neighbor((0, 0), 1, neighbor_mat, style)
    elif u and not r:
        path = style.draw('tip')
        rotate_cell(path, 2)
        path += process_neighbor((0, 0), 2, neighbor_mat, style)
    elif r and u:
        paths = style.draw('turn')
        rotate_cell(paths, 1)
        n1 = process_neighbor((0, 0), 1, neighbor_mat, style)
        n2 = process_neighbor((0, 0), 2, neighbor_mat, style)
        path = paths[1] + n1 + paths[0] + n2

    scale_path(path, spacing)
    translate_path(path, start[0], start[1])
    # if path[0]['command'] == 'L':
    #     path[0]['command'] = 'M'
    # else:
    path.insert(0, dict(command='M', to=path[-1]['to']))
    # path.append(dict(command='Z'))

    return dict(type='path', d=path)


def fill_maze(outline, spacing, style, rotation=None):
    """Fill a region with a maze-like pattern.

    Args:
        outline (dict|list): The shape/s that will become the clip.
        spacing (number): The cell width of the grid.
        draw_fun (function): A maze-drawing function that takes a component keyword and returns one or more paths to be assembled.
        rotation (float|int): The orientation of the grid in degrees.

    Returns:
        A group dict with clip.

    """
    if rotation is not None:
        bounds = rotated_bounding_box(outline, rotation)
    else:
        bounds = bounding_box(outline)
    bounds = add_margin(bounds, 20)

    rows = int(math.ceil((bounds[3] - bounds[2]) / float(spacing)))
    cols = int(math.ceil((bounds[1] - bounds[0]) / float(spacing)))
    fill = maze(rows, cols, spacing, (bounds[0], bounds[2]), style)

    if rotation is not None:
        rotate_shapes(fill, rotation)

    return dict(type='group', clip=outline, members=[fill])


def fill_maze_hue_rotate(outline, spacing, style, color):
    """Fill a region with mazes with hue-dependent orientation.

    Used for texturing image regions so that adjacent regions of
    similar color blend together while contrasting with regions of
    different color.

    Args:
        outline (dict|list): The shape/s that will become the clip.
        spacing (float|int): The cell width of the grid.
        draw_fun (function): A maze-drawing function that takes a component keyword and returns one or more paths to be assembled.
        color (color): The fill color for the maze.

    Returns:
        A group dict with clip.

    """
    rotation = rgb_to_hsl(color)[0] * 90
    # hsl = rgb_to_hsl(color)
    # rotation = (hsl[0] * hsl[1] ** 0.1 * (1 - abs(2 * hsl[2] - 1)) ** 0.1 * 90 + 45) % 90
    x = fill_maze(outline, spacing, style, rotation)
    set_style(x['members'], 'fill', color)
    return x
