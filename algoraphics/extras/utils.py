"""
utils.py
========
Functions used in the extras library.

"""

import numpy as np
from typing import Dict

from ..color import Color, make_color


def _markov_next(state: str, trans_probs: Dict[str, Dict[str, float]]) -> str:
    """Get the next state in a first-order Markov chain.

    Args:
        state: The current state.
        trans_probs: A dictionary of dictionaries containing
          transition probabilities from one state (first key) to
          another (second key).

    Returns:
        The next state.

    """
    states = list(trans_probs[state].keys())
    probs = [trans_probs[state][s] for s in states]
    return np.random.choice(states, p=probs)


def contrasting_lightness(color: Color, light_diff: float) -> Color:
    """Get color with contrasting lightness to reference color.

    Color is lighter if original lightness is < 0.5 and darker otherwise.
    Used to create color pairs for a mixture of light and dark colors.

    Args:
        color: A color.
        light_diff: Magnitude of difference in lightness, between 0 and 1.

    Returns:
        The contrasting color.

    """
    hsl = make_color(color).value()
    if hsl[2] < 0.5:
        new_light = min(hsl[2] + light_diff, 1.0)
    else:
        new_light = max(hsl[2] - light_diff, 0.0)
    new_hsl = (hsl[0], hsl[1], new_light)
    return Color(hsl=new_hsl)

