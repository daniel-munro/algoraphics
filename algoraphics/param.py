"""
param.py
========
Define parameter objects that incorporate randomness.

"""

import numpy as np
from copy import deepcopy
from typing import Union, Callable

Number = Union[int, float]


class Param:
    """Objects to represent fixed or random parameters for shapes.

    Create ``Param`` objects for fixed values, value lists, arbitrary
    functions, and parameters with ``delta`` or ``ratio``.  For random
    distributions, use a specific class that inherits from ``Param``.

    If ``delta`` or ``ratio`` is supplied, ``x`` is the starting value
    if supplied.  Otherwise, if ``min`` and ``max`` are supplied, the
    starting value will be chosen uniformly randomly between them.
    Otherwise, the starting value will be 0 (delta) or 1 (ratio).

    Passing a randomized ``Param`` object to ``delta`` or ``ratio``
    will result in a random walk.  These ``Param`` objects can
    themselves have a ``delta``/``ratio`` argument, resulting in
    higher-order random walks.

    Args:
        x: A value, list, or function that takes no arguments and returns a value.
        delta: A value to add to the previous value to get the next.
        ratio: Similar to delta, but is multiplied by, rather than added to, the previous value to get the next.
        min: The smallest allowable value when ``delta`` or ``ratio`` is used.
        max: The largest allowable value when ``delta`` or ``ratio`` is used.

    """
    def __init__(self, x: Union[str, float, int, list, Callable] = None,
                 delta: Union[Number, Callable, 'Param'] = None,
                 ratio: Union[Number, Callable, 'Param'] = None,
                 min: Number = None, max: Number = None):
        if delta is not None or ratio is not None:
            if x is not None:
                self.last = x
            elif min is not None and max is not None:
                self.last = np.random.uniform(min, max)
            else:
                self.last = 0 if delta is not None else 1
                # raise TypeError("For a Param with delta or ratio, provide "
                #                 + "starting value or min and max.")
        elif type(x) is list:
            self.values = x
            self.value = lambda: np.random.choice(self.values)
            try:
                self.mean = sum(x) / len(x)
            except TypeError:
                True
        elif callable(x):
            self.value = x
        else:
            if min is not None and max is not None:
                raise ValueError("Use min/max only with delta/ratio, or pass "
                                 + "to Uniform.")
            self.value = lambda: x
            self.mean = x

        if delta is not None:
            self.min = min
            self.max = max
            self.delta = delta
            # self.last = self.value()
            self.value = self._value_with_delta
        elif ratio is not None:
            self.min = min
            self.max = max
            self.ratio = ratio
            # self.last = self.value()
            self.value = self._value_with_ratio

    def _value_with_delta(self):
        """Add ``delta`` to get the next value."""
        this_delta = fixed_value(self.delta)
        val = self.last + this_delta
        if self.min is not None:
            val = max(val, self.min)
        if self.max is not None:
            val = min(val, self.max)
        self.last = val
        return val

    def _value_with_ratio(self):
        """Multiply by ``ratio`` to get the next value."""
        this_ratio = fixed_value(self.ratio)
        val = self.last * this_ratio
        if self.min is not None:
            val = max(val, self.min)
        if self.max is not None:
            val = min(val, self.max)
        self.last = val
        return val


class Uniform(Param):
    """Parameters with uniformly random distributions.

    Args:
        min: The lower bound.
        max: The upper bound.

    """
    def __init__(self, min: Number = 0, max: Number = 1):
        self.min = min
        self.max = max
        self.mean = (min + max) / 2

    def value(self):
        """Generate a value."""
        return np.random.uniform(self.min, self.max)


class Normal(Param):
    """Parameters with Gaussian (normal) distributions.

    Args:
        mean: The distribution's mean.
        stdev: The distribution's standard deviation.

    """
    def __init__(self, mean: Number = 0, stdev: Number = 1):
        self.mean = mean
        self.stdev = stdev

    def value(self):
        """Generate a value."""
        return np.random.normal(self.mean, self.stdev)


class Exponential(Param):
    """Paramaters with Exponential distributions.

    Args:
        mean: The distribution's mean.
        stdev: The distribution's standard deviation.
        sigma: How many standard deviations from the mean to clip values.

    """
    def __init__(self, mean=1, stdev=1, sigma=2):
        self.mean = mean
        self.stdev = 1
        self.min = mean - sigma * stdev
        self.max = mean + sigma * stdev

    def value(self):
        """Generate a value."""
        x = (self.mean - self.stdev) + np.random.exponential(self.stdev)
        # x = np.clip(x, self.min, self.max)
        return x


def fixed_value(x: Union[Number, str, Param]) -> Union[Number, str]:
    """Get a fixed value if a ``Param`` object is supplied.

    """
    if isinstance(x, Param):
        return x.value()
    else:
        return x


def make_param(x: Union[Number, str, Param]) -> Param:
    """Get a ``Param`` object if something else is supplied.

    If a ``Param`` object is supplied, a deep copy is generated in
    case it has a ``delta`` or ``ratio`` and is being reused.

    """
    if isinstance(x, Param):
        # Copy in case it is random walk and user reuses it.
        return(deepcopy(x))
    else:
        return Param(x)
