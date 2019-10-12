"""
mazes.py
========
Functions for creating maze-like patterns.

"""

import numpy as np
import copy
from typing import Sequence, Tuple, Union

from ..main import add_margin
from ..shapes import (
    bounding_box,
    rotated_bounding_box,
    rotate_shapes,
    Shape,
    Polygon,
    Spline,
    Group,
)
from ..geom import rotate_points, translate_points, scale_points, rad, deg
from .grid import grid_tree_neighbors
from .utils import points_on_line, points_on_arc


# Number = Union[int, float]
# Point = Tuple[Number, Number]
Pnt = Tuple[float, float]
Collection = Union[list, Shape, Group]


def _rotated_piece(path: Sequence[dict], times: int) -> Sequence[dict]:
    """Get a rotated copy of a maze piece."""
    path = copy.deepcopy(path)
    _rotate_cell(path, times)
    return path


class Maze_Style:
    """Specifications for maze styles.

    Built-in styles inherit from this class, and custom styles can be
    made to do so as well.  It must implement the tip, turn, straight,
    T, and cross methods to describe how each component is drawn.

    Each of these methods should generate forms for one cell of the
    maze.  They must provide one or more pieces which are stitched
    together when the maze is assembled.  For example, for a cell in
    which the maze turns right, the inner and outer edges of the curve
    are generated.  Once this cell is encountered in the stitching
    process, the inner edge is added, then everything from the cell to
    the right is recursively added, and then the outer edge is added
    to get one continuous edge.

    For all methods the edge enters below and draws the component
    counter-clockwise.  During maze generation components are
    generated and then rotated as needed to accomodate any combination
    of neighbors that the cell should connect to.

    """

    def _raise_error(self):
        raise NotImplementedError(
            "Your maze style must have tip, turn, straight, T, and cross functions."
        )

    def output(self, points):
        """Make the output shape/s from the generated points.

        This takes the maze outline points and produces the intended
        shape/s, e.g. polygon or spline.  Returns a polygon by
        default.

        """
        return Polygon(points)

    def tip(self):
        """Generate a dead-end cell.

        This should return a list of path command dictionaries.

        """
        self._raise_error()

    def turn(self):
        """Generate a right turn cell.

        This should return a tuple of two lists of path commands
        corresponding to the inner and then outer edges.

        Left turns will be drawn with this and then rotated.

        """
        self._raise_error()

    def straight(self):
        """Generate a non-turning cell.

        This should return a tuple of two lists of path commands
        corresponding to the right and then left edges.

        """
        self._raise_error()

    def T(self):
        """Generate a 'T'-shaped cell.

        This should return a tuple of three lists of path commands
        corresponding to the right inner edge, top edge, and then left
        inner edge.

        """
        self._raise_error()

    def cross(self):
        """Generate a cell connecting in all directions.

        This should return a tuple of four lists of path commands
        corresponding to the lower-right, upper-right, upper-left, and
        lower-left inner edges.

        """
        self._raise_error()


class Maze_Style_Pipes(Maze_Style):
    """Generate pieces for curved pipes.

    Args:
        rel_thickness: Channel width relative to cell width, from 0 to 1.

    """

    def __init__(self, rel_thickness: float):
        self.rel_thickness = rel_thickness
        self.w = rel_thickness / 2

    def output(self, points):
        return Spline(points)

    def right_turn(self):
        """"""
        r_in = (0.5 - self.w) * self.rel_thickness  # inner curve radius
        p1 = (0.5 + self.w, 0)
        p2 = (0.5 + self.w, 0.5 - self.w - r_in)
        x = points_on_line(p1, p2, 0.1)[:-1]
        c = (0.5 + self.w + r_in, 0.5 - self.w - r_in)
        x += points_on_arc(c, r_in, 180, 90, 0.03)[:-1]
        p1 = (0.5 + self.w + r_in, 0.5 - self.w)
        p2 = (1, 0.5 - self.w)
        x += points_on_line(p1, p2, 0.1)[:-1]
        return x

    def tip(self):
        """"""
        x = points_on_line((0.5 + self.w, 0), (0.5 + self.w, 0.5), self.w / 2)[:-1]
        x += points_on_arc((0.5, 0.5), self.w, 0, 180, self.w / 2)[:-1]
        x += points_on_line((0.5 - self.w, 0.5), (0.5 - self.w, 0), self.w / 2)[:-1]
        return x

    def turn(self):
        """"""
        x1 = self.right_turn()
        x2 = points_on_line((1, 0.5 + self.w), (0.5, 0.5 + self.w), 0.1)[:-1]
        x2 += points_on_arc((0.5, 0.5), self.w, 90, 180, self.w / 2)[:-1]
        x2 += points_on_line((0.5 - self.w, 0.5), (0.5 - self.w, 0), 0.1)[:-1]
        return (x1, x2)

    def straight(self):
        """"""
        x1 = [(0.5 + self.w, 0.1), (0.5 + self.w, 0.9)]
        x2 = [(0.5 - self.w, 0.9), (0.5 - self.w, 0.1)]
        return (x1, x2)

    def T(self):
        """"""
        x1 = self.right_turn()
        x2 = [(0.9, 0.5 + self.w), (0.1, 0.5 + self.w)]
        x3 = _rotated_piece(x1, 3)
        return (x1, x2, x3)

    def cross(self):
        """"""
        x1 = self.right_turn()
        x2 = _rotated_piece(x1, 1)
        x3 = _rotated_piece(x1, 2)
        x4 = _rotated_piece(x1, 3)
        return (x1, x2, x3, x4)


class Maze_Style_Round(Maze_Style):
    """Generate pieces for very curvy pipes.

    Args:
        rel_thickness: Channel width relative to cell width, from 0 to 1.

    """

    def __init__(self, rel_thickness: float):
        self.w = rel_thickness / 2

    def output(self, points):
        return Spline(points)

    def right_turn(self):
        """"""
        pts = points_on_arc((1, 0), 0.5 - self.w, 180, 90, (0.5 - self.w) / 2)[:-1]
        return pts

    def tip(self):
        """"""
        pts = points_on_line((0.5 + self.w, 0), (0.5 + self.w, 0.5), 0.2)[:-1]
        pts += points_on_arc((0.5, 0.5), self.w, 0, 180, self.w / 4)[:-1]
        pts += points_on_line((0.5 - self.w, 0.5), (0.5 - self.w, 0), 0.2)[:-1]
        return pts

    def turn(self):
        """"""
        inner = self.right_turn()
        outer = points_on_arc((1, 0), 0.5 + self.w, 90, 180, 0.2)[:-1]
        return (inner, outer)

    def straight(self):
        """"""
        right = [(0.5 + self.w, 0.1), (0.5 + self.w, 0.9)]
        left = [(0.5 - self.w, 0.9), (0.5 - self.w, 0.1)]
        return (right, left)

    def T(self):
        """"""
        right = self.right_turn()
        # p = (0.5, math.sqrt((0.5 + self.w) ** 2 - 0.5 ** 2))
        theta = deg(np.arccos(0.5 / (0.5 + self.w)))
        top = points_on_arc((1, 0), 0.5 + self.w, 90, 180 - theta, 0.2)
        top += points_on_arc((0, 0), 0.5 + self.w, theta, 90, 0.2)[:-1]
        left = _rotated_piece(right, 3)
        return (right, top, left)

    def cross(self):
        """"""
        pts1 = [(0.5 + self.w, 0.5 - self.w), (1, 0.5 - self.w)]
        pts1 = points_on_line((0.5 + self.w, 0), (0.5 + self.w, 0.5 - self.w), 0.2)
        pts1 += points_on_line((0.5 + self.w, 0.5 - self.w), (1, 0.5 - self.w), 0.2)
        pts2 = _rotated_piece(pts1, 1)
        pts3 = _rotated_piece(pts1, 2)
        pts4 = _rotated_piece(pts1, 3)
        return (pts1, pts2, pts3, pts4)


class Maze_Style_Straight(Maze_Style):
    """Generate pieces for simple right-angle maze.

    Args:
        rel_thickness: Channel width relative to cell width, from 0 to 1.

    """

    def __init__(self, rel_thickness: float):
        self.w = rel_thickness / 2

    def output(self, points):
        return Polygon(points)

    def tip(self):
        """"""
        w = self.w
        pts = [(0.5 + w, 0.5 + w), (0.5 - w, 0.5 + w)]
        return pts

    def turn(self):
        """"""
        w = self.w
        inner = [(0.5 + w, 0.5 - w)]
        outer = [(0.5 - w, 0.5 + w)]
        return (inner, outer)

    def straight(self):
        """"""
        return ([], [])

    def T(self):
        """"""
        w = self.w
        right = [(0.5 + w, 0.5 - w)]
        left = [(0.5 - w, 0.5 - w)]
        return (right, [], left)

    def cross(self):
        """"""
        w = self.w
        pt1 = [(0.5 + w, 0.5 - w)]
        pt2 = [(0.5 + w, 0.5 + w)]
        pt3 = [(0.5 - w, 0.5 + w)]
        pt4 = [(0.5 - w, 0.5 - w)]
        return (pt1, pt2, pt3, pt4)


class Maze_Style_Jagged(Maze_Style):
    """Generate pieces for jagged maze.

    Args:
        min_w: Minimum width of channel segment relative to cell width.
        max_w: Maximum width of channel segment relative to cell width.

    """

    def __init__(self, min_w: float, max_w: float):
        self.min_w = min_w
        self.max_w = max_w

    def output(self, points):
        return Polygon(points)

    def dev(self):
        return np.random.uniform(self.min_w / 2, self.max_w / 2)

    def big_dev(self):
        return np.random.uniform(-self.max_w / 2, self.max_w / 2)

    def tip(self):
        """"""
        dev = self.dev
        pts = [(0.5 + dev(), 0.5 + dev()), (0.5 - dev(), 0.5 + dev())]
        return pts

    def turn(self):
        """"""
        dev = self.dev
        inner = [(0.5 + dev(), 0.5 - dev())]
        outer = [(0.5 - dev(), 0.5 + dev())]
        return (inner, outer)

    def straight(self):
        """"""
        dev = self.dev
        right = [(0.5 + dev(), 0.5 + self.big_dev())]
        left = [(0.5 - dev(), 0.5 + self.big_dev())]
        return (right, left)

    def T(self):
        """"""
        dev = self.dev
        right = [(0.5 + dev(), 0.5 - dev())]
        top = [(0.5 + self.big_dev(), 0.5 + dev())]
        left = [(0.5 - dev(), 0.5 - dev())]
        return (right, top, left)

    def cross(self):
        """"""
        dev = self.dev
        pt1 = [(0.5 + dev(), 0.5 - dev())]
        pt2 = [(0.5 + dev(), 0.5 + dev())]
        pt3 = [(0.5 - dev(), 0.5 + dev())]
        pt4 = [(0.5 - dev(), 0.5 - dev())]
        return (pt1, pt2, pt3, pt4)


def _new_coords(prev_coords: Tuple[int, int], direction: int) -> Tuple[int, int]:
    """Get new grid coordinates after moving one step.

    Args:
        prev_coords: The starting (r, c) coordinates.
        direction: Direction of movement (0=d, 1=r, 2=u, 3=l).

    Returns:
        The new grid coordinates.

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


def _rotate_cell(points: Union[Sequence[Pnt], Tuple[Sequence[Pnt], ...]], times: int):
    """Rotate points at right angles within grid cell.

    Args:
        points: A point list or tuple of point lists.
        times: Number of 90 degree counter-clockwise turns.

    """
    times = times % 4
    if type(points) is not tuple:
        points = (points,)
    if times > 0:
        for p in points:
            rotate_points(p, (0.5, 0.5), rad(times * 90))


def _translate_cell(
    points: Union[Sequence[Pnt], Tuple[Sequence[Pnt], ...]], coords: Tuple[int, int]
):
    """Translate points to grid coordinate.

    Treats grid cells as having width 1.

    Args:
        points: A point list or tuple of point lists.
        coords: The (r, c) coordinates to move to.

    """
    if type(points) is not tuple:
        points = (points,)
    for p in points:
        translate_points(p, coords[1], coords[0])


def _process_neighbor(
    coords: Tuple[int, int], direc: int, neighbor_mat: np.ndarray, style: Maze_Style
) -> list:
    """Call ``draw_cell()`` on neighboring cell.

    Args:
        coords: The current (r, c) coordinates.
        direc: Direction of neighbor to process (0=d, 1=r, 2=u, 3=l).
        neighbor_mat: A boolean array with dimensions (rows, cols, 4)
          indicating if neighboring cells are connected.
        style: An object specifying how the maze path is to be drawn.

    Returns:
        Point list for neighboring subtree.

    """
    coords2 = _new_coords(coords, direc % 4)
    return _draw_cell(coords2, (direc + 2) % 4, neighbor_mat, style)


def _draw_cell(
    coords: Tuple[int, int], dir_from: int, neighbor_mat: np.ndarray, style: Maze_Style
) -> list:
    """Get the subtree points recursively for a cell.

    Args:
        coords: The current (r, c) coordinates.

        dir_from: Direction from which cell was entered (returned
          subtree will include the remaining connected directions).
        neighbor_mat: boolean array with dimensions (rows, cols, 4)
          indicating if neighboring cells are connected.
        style: An object specifying how the maze path is to be drawn.

    Returns:
        Point list for subtree that excludes everything in the
        originating direction.

    """
    neighbors = neighbor_mat[coords]
    r = neighbors[(dir_from + 1) % 4]
    s = neighbors[(dir_from + 2) % 4]
    le = neighbors[(dir_from + 3) % 4]

    # U-turn:
    if not r and not s and not le:
        path = style.tip()
        _rotate_cell(path, dir_from)
        _translate_cell(path, coords)

    # right turn:
    elif r and not s and not le:
        paths = style.turn()
        _rotate_cell(paths, dir_from)
        _translate_cell(paths, coords)
        n = _process_neighbor(coords, dir_from + 1, neighbor_mat, style)
        path = paths[0] + n + paths[1]

    # left turn:
    elif not r and not s and le:
        paths = style.turn()
        _rotate_cell(paths, dir_from + 3)
        _translate_cell(paths, coords)
        n = _process_neighbor(coords, dir_from + 3, neighbor_mat, style)
        path = paths[1] + n + paths[0]

    # straight:
    elif not r and s and not le:
        paths = style.straight()
        _rotate_cell(paths, dir_from)
        _translate_cell(paths, coords)
        n = _process_neighbor(coords, dir_from + 2, neighbor_mat, style)
        path = paths[0] + n + paths[1]

    # T:
    elif r and not s and le:
        paths = style.T()
        _rotate_cell(paths, dir_from)
        _translate_cell(paths, coords)
        n1 = _process_neighbor(coords, dir_from + 1, neighbor_mat, style)
        n2 = _process_neighbor(coords, dir_from + 3, neighbor_mat, style)
        path = paths[0] + n1 + paths[1] + n2 + paths[2]

    elif r and s and not le:
        paths = style.T()
        _rotate_cell(paths, dir_from + 1)
        _translate_cell(paths, coords)
        n1 = _process_neighbor(coords, dir_from + 1, neighbor_mat, style)
        n2 = _process_neighbor(coords, dir_from + 2, neighbor_mat, style)
        path = paths[2] + n1 + paths[0] + n2 + paths[1]

    elif not r and s and le:
        paths = style.T()
        _rotate_cell(paths, dir_from + 3)
        _translate_cell(paths, coords)
        n1 = _process_neighbor(coords, dir_from + 2, neighbor_mat, style)
        n2 = _process_neighbor(coords, dir_from + 3, neighbor_mat, style)
        path = paths[1] + n1 + paths[2] + n2 + paths[0]

    # cross:
    elif r and s and le:
        paths = style.cross()
        _rotate_cell(paths, dir_from)
        _translate_cell(paths, coords)
        n1 = _process_neighbor(coords, dir_from + 1, neighbor_mat, style)
        n2 = _process_neighbor(coords, dir_from + 2, neighbor_mat, style)
        n3 = _process_neighbor(coords, dir_from + 3, neighbor_mat, style)
        path = paths[0] + n1 + paths[1] + n2 + paths[2] + n3 + paths[3]

    return path


def maze(
    rows: int, cols: int, spacing: float, start: Pnt, style: Maze_Style
) -> Collection:
    """Generate a maze-like pattern spanning the specified grid.

    Args:
        rows: Number of rows in the grid.
        cols: Number of columns in the grid.
        spacing: The cell width.
        start: The bottom-left coordinate of the grid.
        style: An object specifying how the maze path is to be drawn.

    Returns:
        A shape (usually a spline or polygon) or collection.

    """
    neighbor_mat = grid_tree_neighbors(rows, cols)
    r = neighbor_mat[0, 0, 1]
    u = neighbor_mat[0, 0, 2]

    if r and not u:
        path = style.tip()
        _rotate_cell(path, 1)
        path += _process_neighbor((0, 0), 1, neighbor_mat, style)
    elif u and not r:
        path = style.tip()
        _rotate_cell(path, 2)
        path += _process_neighbor((0, 0), 2, neighbor_mat, style)
    elif r and u:
        paths = style.turn()
        _rotate_cell(paths, 1)
        n1 = _process_neighbor((0, 0), 1, neighbor_mat, style)
        n2 = _process_neighbor((0, 0), 2, neighbor_mat, style)
        path = paths[1] + n1 + paths[0] + n2

    scale_points(path, spacing)
    translate_points(path, start[0], start[1])

    return style.output(path)


def fill_maze(
    outline: Collection, spacing: float, style: Maze_Style, rotation: float = None
) -> dict:
    """Fill a region with a maze-like pattern.

    Args:
        outline: The shape/s that will become the clip.
        spacing: The cell width of the grid.
        style: An object specifying how the maze path is to be drawn.
        rotation: The orientation of the grid in degrees.

    Returns:
        A group with clip.

    """
    if rotation is not None:
        bounds = rotated_bounding_box(outline, rotation)
    else:
        bounds = bounding_box(outline)
    bounds = add_margin(bounds, 20)

    rows = int(np.ceil((bounds[3] - bounds[1]) / float(spacing)))
    cols = int(np.ceil((bounds[2] - bounds[0]) / float(spacing)))
    fill = maze(rows, cols, spacing, (bounds[0], bounds[1]), style)

    if rotation is not None:
        rotate_shapes(fill, rotation)

    return Group(clip=outline, members=[fill])
