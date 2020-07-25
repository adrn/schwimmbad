# Standard library
from itertools import starmap

# Project
from .pool import BasePool

__all__ = ['SerialPool']

class SerialPool(BasePool):
    """A serial pool that wraps the built-in :func:`map` function.

    Parameters
    ----------
    None

    """

    def __init__(self, **kwargs):
        self.size = 0
        self.rank = 0

    @staticmethod
    def enabled():
        return True

    def map(self, func, iterable, callback=None):
        """A wrapper around the built-in ``map()`` function to provide a
        consistent interface with the other ``Pool`` classes.

        Parameters
        ----------
        worker : callable
            A function or callable object that is executed on each element of
            the specified ``tasks`` iterable. This object must be picklable
            (i.e. it can't be a function scoped within a function or a
            ``lambda`` function). This should accept a single positional
            argument and return a single object.
        tasks : iterable
            A list or iterable of tasks. Each task can be itself an iterable
            (e.g., tuple) of values or data to pass in to the worker function.
        callback : callable, optional
            An optional callback function (or callable) that is called with the
            result from each worker run and is executed on the master process.
            This is useful for, e.g., saving results to a file, since the
            callback is only called on the master thread.

        Returns
        -------
        results : generator

        """
        return self._call_callback(callback, map(func, iterable))

    def starmap(self, func, iterable, callback=None):
        return self._call_callback(callback, starmap(func, iterable))
