"""
param.py
========
Define parameter objects that incorporate randomness.

"""

import numpy as np
from copy import deepcopy


class Param:
    def __init__(self, x=None, delta=None, ratio=None, min=None, max=None):
        """
        Args:
            delta (float|function|Param): A value to add to the previous value to get the next.  If provided, the other arguments will be used to generate the initial value and are then ignored.  Passing a randomized Param object will result in a random walk.  These Param objects can themselves have a delta argument, resulting in higher-order random walks.
            ratio (float|function|Param): Similar to delta, but is multiplied by, rather than added to, the previous value to get the next.

        """
        if delta is not None or ratio is not None:
            if x is not None:
                self.last = x
            elif min is not None and max is not None:
                self.last = np.random.uniform(min, max)
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
            self.value = lambda: x
            self.mean = x

        if delta is not None:
            self.min = min
            self.max = max
            self.delta = delta
            # self.last = self.value()
            self.value = self.value_with_delta
        elif ratio is not None:
            self.min = min
            self.max = max
            self.ratio = ratio
            # self.last = self.value()
            self.value = self.value_with_ratio

    def value_with_delta(self):
        this_delta = fixed_value(self.delta)
        val = self.last + this_delta
        if self.min is not None:
            val = max(val, self.min)
        if self.max is not None:
            val = min(val, self.max)
        self.last = val
        return val

    def value_with_ratio(self):
        this_ratio = fixed_value(self.ratio)
        val = self.last * this_ratio
        if self.min is not None:
            val = max(val, self.min)
        if self.max is not None:
            val = min(val, self.max)
        self.last = val
        return val


class Uniform(Param):
    def __init__(self, min=0, max=1):
        self.min = min
        self.max = max
        self.mean = (min + max) / 2

    def value(self):
        return np.random.uniform(self.min, self.max)


class Normal(Param):
    def __init__(self, mean=0, stdev=1):
        self.mean = mean
        self.stdev = stdev

    def value(self):
        return np.random.normal(self.mean, self.stdev)


class Exponential(Param):
    def __init__(self, mean=1, stdev=1, sigma=2):
        self.mean = mean
        self.stdev = 1
        self.min = mean - sigma * stdev
        self.max = mean + sigma * stdev

    def value(self):
        x = (self.mean - self.stdev) + np.random.exponential(self.stdev)
        # x = np.clip(x, self.min, self.max)
        return x


def fixed_value(x):
    if isinstance(x, Param):
        return x.value()
    else:
        return x


def make_param(x):
    if isinstance(x, Param):
        # Copy in case it is random walk and user reuses it.
        return(deepcopy(x))
    else:
        return Param(x)
