"""
grid.py
=======
Functions for working with grids.

"""

import numpy as np
import matplotlib.colors
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree, shortest_path
from typing import Sequence, Tuple

from ..color import Color, make_color


def rgb_array_to_hsv(rgb: np.ndarray) -> np.ndarray:
    """Convert matrix of rgb values to HSV.

    Args:
        rgb: An array of rgb colors.

    Returns:
        An array of HSV colors.
    """
    return matplotlib.colors.rgb_to_hsv(rgb)


def hsv_array_to_rgb(hsv: np.ndarray) -> np.ndarray:
    """Convert matrix of HSV values to rgb.

    Args:
        hsv: An array of HSV colors.

    Returns:
        An array of rgb colors.
    """
    return matplotlib.colors.hsv_to_rgb(hsv)


def map_colors_to_array(
    values: np.ndarray, colors: Sequence[Color], gradient_mode: str = "rgb"
) -> np.ndarray:
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
    if gradient_mode == "hsv":
        colors = rgb_array_to_hsv(np.array([colors]))[0, :]

    # Get the two colors per pixel to be mixed:
    color1 = values.astype(int)
    color2 = ((values + 1) % len(colors)).astype(int)
    proportion = values % 1
    c1 = colors[color1]
    c2 = colors[color2]

    if gradient_mode == "rgb":
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
    out = (out * 255).astype("uint8")
    return out


def grid_tree(rows: int, cols: int) -> np.ndarray:
    """Generate random spanning tree for a grid.

    Tree connects adjacent elements of a grid. Used for pixels and for
    other grids.

    Args:
        rows: Number of rows in the grid.
        cols: Number of columns in the grid.

    Returns:
        A 2D binary array in sparse format with dimensions (num. grid
        cells x num. grid cells) indicating which cells are connected.

    """
    right_edges = [((r, c), (r, c + 1)) for r in range(rows) for c in range(cols - 1)]
    up_edges = [((r, c), (r + 1, c)) for r in range(rows - 1) for c in range(cols)]
    node1, node2 = tuple(zip(*(right_edges + up_edges)))
    node1 = [r * cols + c for (r, c) in node1]
    node2 = [r * cols + c for (r, c) in node2]
    weight = np.random.random(len(node1))
    mat = csr_matrix((weight, (node1, node2)), (rows * cols, rows * cols))
    return minimum_spanning_tree(mat).ceil().astype(int)


def grid_tree_edges(
    rows: int, cols: int
) -> Sequence[Tuple[Tuple[int, int], Tuple[int, int]]]:
    """Generate edges of a random spanning tree for a grid.

    Args:
        rows: Number of rows in the grid.
        cols: Number of columns in the grid.

    Returns:
        A list of ((r1, c1), (r2, c2)) coordinate tuple pairs.

    """
    tree_mat = grid_tree(rows, cols)
    nonzero = zip(*tree_mat.nonzero())
    return [((n1 // cols, n1 % cols), (n2 // cols, n2 % cols)) for (n1, n2) in nonzero]


def grid_tree_neighbors(rows: int, cols: int) -> np.ndarray:
    """Generate a random spanning tree for a grid and return neighbor array.

    Args:
        rows: Number of rows in grid.
        cols: Number of cols in grid.

    Returns:
        A 3D boolean array (rows x cols x [d?, r?, u?, l?]).  The
        third dimension is length 4 and indicates whether that cell
        shares an edge with the cell below, right, above, and left of
        it.

    """

    def connected(coords1, coords2, edges):
        return (coords1, coords2) in edges or (coords2, coords1) in edges

    edges = grid_tree_edges(rows, cols)
    x = np.empty((rows, cols, 4), dtype=bool)
    for r in range(rows):
        for c in range(cols):
            x[r, c, 0] = r > 0 and connected((r, c), (r - 1, c), edges)
            x[r, c, 1] = c < cols - 1 and connected((r, c), (r, c + 1), edges)
            x[r, c, 2] = r < rows - 1 and connected((r, c), (r + 1, c), edges)
            x[r, c, 3] = c > 0 and connected((r, c), (r, c - 1), edges)

    return x


def grid_tree_dists(rows: int, cols: int) -> np.ndarray:
    """Generate an array of random spanning tree distances.

    Each value is the distance to (0, 0) along a spanning tree.  Map
    to a cyclical color gradient to create a billowing effect.

    Args:
        rows: Number of rows in the grid.
        cols: Number of columns in the grid.

    Returns:
        A 2D array of integers.

    """
    tree_mat = grid_tree(rows, cols)
    dists = shortest_path(tree_mat, directed=False, unweighted=True, indices=0)
    return np.reshape(dists, (rows, cols))
