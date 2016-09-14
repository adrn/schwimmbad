# Standard library
from __future__ import division, print_function, absolute_import, unicode_literals
import signal
import functools
import multiprocessing
from multiprocessing.pool import Pool

# Project
from . import log, VERBOSE

def _initializer_wrapper(actual_initializer, *rest):
    """
    We ignore SIGINT. It's up to our parent to kill us in the typical
    condition of this arising from ``^C`` on a terminal. If someone is
    manually killing us with that signal, well... nothing will happen.

    """
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    if actual_initializer is not None:
        actual_initializer(*rest)

class MultiPool(Pool):
    """
    A modified version of :class:`multiprocessing.pool.Pool` that has better
    behavior with regard to ``KeyboardInterrupts`` in the :func:`map` method.

    (Original author: Peter K. G. Williams <peter@newton.cx>)

    Parameters
    ----------
    processes : int (optional)
        The number of worker processes to use; defaults to the number of CPUs.
    initializer : callable (optional)
        Either ``None``, or a callable that will be invoked by each worker
        process when it starts.
    initargs : iterable (optional)
        Arguments for *initializer*; it will be called as
        ``initializer(*initargs)``.
    kwargs: (optional)
        Extra arguments passed to the :class:`multiprocessing.pool.Pool`
        superclass.

    """
    wait_timeout = 3600

    def __init__(self, processes=None, initializer=None, initargs=(), **kwargs):
        new_initializer = functools.partial(_initializer_wrapper, initializer)
        super(MultiPool, self).__init__(processes, new_initializer,
                                        initargs, **kwargs)
        self.size = 0

    @staticmethod
    def enabled():
        return True

    def map(self, func, iterable, chunksize=None, callback=None):
        """
        Equivalent to the built-in ``map()`` function and
        :meth:`multiprocessing.pool.Pool.map()`, without catching
        ``KeyboardInterrupt``.

        Parameters
        ----------
        func : callable
            The function or callable to apply to the items. This should accept
            a single positional argument and return a single object.
        iterable : iterable
            An iterable of items that will have ``func`` applied to them.
        callback : callable (optional)
            An optional callback function that is called after the map'ped
            function returns but before the results are returned. The
            callback function is called on the master process so it is
            safe to write to files from the callback function.

        """

        # The key magic is that we must call r.get() with a timeout, because
        # a Condition.wait() without a timeout swallows KeyboardInterrupts.
        r = self.map_async(func, iterable, chunksize=chunksize, callback=callback)

        while True:
            try:
                return r.get(self.wait_timeout)

            except multiprocessing.TimeoutError:
                pass

            except KeyboardInterrupt:
                self.terminate()
                self.join()
                raise
