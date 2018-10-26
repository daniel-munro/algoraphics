"""
trees.py
========
Generate trees.

"""

import random

from .geom import rad, endpoint


def tree(start, direction, l_min, l_max, theta, p, p_delta):
    """Generate a tree with randomly terminating branches.

    Args:
        start (point): The starting point.
        direction (float|int): The starting direction (in degrees).
        l_min (float|int): Minimum branch length.
        l_max (float|int): Maximum branch length.
        theta (float|int): The angle (in degrees) between sibling branches.
        p (float): The starting probability that a given branch will split instead of terminating.
        p_delta (float): The value subtracted from p cumulatively at each branching level.

    Returns:
        list: A list of line shapes.

    """
    angle = rad(direction)
    length = random.uniform(l_min, l_max)
    end = endpoint(start, angle, length)
    x = [dict(type='line', p1=start, p2=end)]
    if random.random() < p:
        x.extend(tree(end, direction + theta / 2., l_min, l_max,
                      theta, p - p_delta, p_delta))
        x.extend(tree(end, direction - theta / 2., l_min, l_max,
                      theta, p - p_delta, p_delta))
    return x
