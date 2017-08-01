# -*- coding: utf-8 -*-

from __future__ import division, print_function

try:
    from joblib import Parallel, delayed
except ImportError:
    Parallel = None

from .pool import BasePool

__all__ = ["JoblibPool"]

class JoblibPool(BasePool):

    def __init__(self, *args, **kwargs):
        if Parallel is None:
            raise ImportError("joblib is required to use the JoblibPool")
        self.args = args
        self.kwargs = kwargs
        self.size = 0
        self.rank = 0

    @staticmethod
    def enabled():
        return Parallel is not None

    def map(self, func, iterable, callback=None):
        dfunc = delayed(func)
        res = Parallel(*(self.args), **(self.kwargs))(
            dfunc(a) for a in iterable
        )
        return self._call_callback(callback, res)
