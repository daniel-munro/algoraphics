"""
trees.py
========
Generate trees.

"""

import random

from .geom import rad, endpoint
from .param import fixed_value, make_param


def tree(start, direction, branch_length, theta, p):
    """Generate a tree with randomly terminating branches.

    Args:
        start (tuple): The starting point.
        direction (float|int): The starting direction (in degrees).
        branch_length (Param): Branch length.
        theta (Param): The angle (in degrees) between sibling branches.
        p (float): The probability that a given branch will split instead of terminating.  Recommended to have a delta < 0 or ratio < 1 so that the tree is guaranteed to terminate.

    Returns:
        list: A list of line shapes.

    """
    start = fixed_value(start)
    direction = fixed_value(direction)
    branch_length = make_param(branch_length)
    theta = make_param(theta)
    p = make_param(p)

    length = branch_length.value()
    end = endpoint(start, rad(direction), length)
    x = [dict(type='line', p1=start, p2=end)]
    if random.random() < p.value():
        theta_this = theta.value()
        x.extend(tree(end, direction + theta_this / 2, branch_length,
                      theta, p))
        x.extend(tree(end, direction - theta_this / 2, branch_length,
                      theta, p))
    return x
