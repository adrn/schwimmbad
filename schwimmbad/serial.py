# Standard library
from __future__ import division, print_function, absolute_import, unicode_literals

# Project
from .pool import BasePool

class SerialPool(BasePool):

    def __init__(self, **kwargs):
        self.size = 0
        self.rank = 0

    @staticmethod
    def enabled():
        return True

    def map(self, func, iterable, callback=None):
        """
        A wrapper around the built-in ``map()`` function to provide a
        consistent interface with the other ``Pool`` classes.

        Parameters
        ----------
        func : callable
            The function to apply to the items.
        iterable : iterable
            An iterable of items that will have ``func`` applied to them.
        callback : callable (optional)
            An optional callback function that is called after the map'ped
            function returns but before the results are returned.

        """
        return self._call_callback(callback, map(func, iterable))
