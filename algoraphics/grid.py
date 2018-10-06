"""
grid.py
=======
Functions involving grids, whether the cells are pixels or otherwise.

"""

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree, shortest_path


def grid_tree(rows, cols):
    """Generate random spanning tree for a grid.

    Tree connects adjacent elements of a grid. Used for pixels and for
    other grids.

    Args:
        rows (int): Number of rows in grid.
        cols (int): Number of cols in grid.

    Returns:
        A 2D binary array with dimensions in sparse format indicating
        which cells are connected.

    """
    right_edges = [((r, c), (r, c + 1)) for r in range(rows) for c in
                   range(cols - 1)]
    up_edges = [((r, c), (r + 1, c)) for r in range(rows - 1) for c in
                range(cols)]
    node1, node2 = tuple(zip(*(right_edges + up_edges)))
    node1 = [r * cols + c for (r, c) in node1]
    node2 = [r * cols + c for (r, c) in node2]
    weight = np.random.random(len(node1))
    mat = csr_matrix((weight, (node1, node2)), (rows * cols, rows * cols))
    return minimum_spanning_tree(mat).ceil().astype(int)


def grid_tree_edges(rows, cols):
    """Generate edges of random spanning tree for a grid.

    Args:
        rows (int): Number of rows in grid.
        cols (int): Number of cols in grid.

    Returns:
        A list of ((r1, c1), (r2, c2)) coordinate tuple pairs.

    """
    tree_mat = grid_tree(rows, cols)
    nonzero = zip(*tree_mat.nonzero())
    return [((n1 // cols, n1 % cols), (n2 // cols, n2 % cols)) for
            (n1, n2) in nonzero]


def grid_tree_neighbors(rows, cols):
    """Generate random spanning tree for a grid and return neighbor array.

    Args:
        rows (int): Number of rows in grid.
        cols (int): Number of cols in grid.

    Returns:
        A 3D boolean array (rows x cols x [d?, r?, u?, l?]).

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


def grid_tree_dists(rows, cols):
    """Generate array of random spanning tree distances.

    Each value is the distance to (0, 0) along a spanning tree.  Map a
    cyclical color gradient to create a billowing effect.

    Args:
        rows (int): Number of rows in grid.
        cols (int): Number of cols in grid.

    Returns:
        A 2D array of integers.

    """
    tree_mat = grid_tree(rows, cols)
    dists = shortest_path(tree_mat, directed=False, unweighted=True, indices=0)
    return np.reshape(dists, (rows, cols))
