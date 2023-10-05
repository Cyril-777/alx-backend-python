#!/usr/bin/env python3
"""
A type-annotated function 'sum_mixed_list' that takes a list 'mxd_lst'
of integers and floats and returns their sum as a float.
"""

from typing import List, Union


def sum_mixed_list(mxd_lst: List[Union[int, float]]) -> float:
    """
    Returns the sum of the list of integers and floats as a float
    """
    return sum(mxd_lst)
