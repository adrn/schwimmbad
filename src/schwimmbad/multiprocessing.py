# type: ignore
import functools
import signal

import multiprocess
from multiprocess.pool import Pool

__all__ = ["MultiPool"]


def _initializer_wrapper(actual_initializer, *rest):
    """
    We ignore SIGINT. It's up to our parent to kill us in the typical
    condition of this arising from ``^C`` on a terminal. If someone is
    manually killing us with that signal, well... nothing will happen.

    """
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    if actual_initializer is not None:
        actual_initializer(*rest)


class CallbackWrapper:
    def __init__(self, callback):
        self.callback = callback

    def __call__(self, tasks):
        for task in tasks:
            self.callback(task)


class MultiPool(Pool):
    """
    A modified version of :class:`multiprocess.pool.Pool` that has better
    behavior with regard to ``KeyboardInterrupts`` in the :func:`map` method.

    NOTE: This is no longer built off of the standard library
    :class:`multiprocessing.pool.Pool` -- this uses the version from `multiprocess`,
    which uses `dill` to pickle objects instead of the standard library `pickle`.

    Parameters
    ----------
    processes : int, optional
        The number of worker processes to use; defaults to the number of CPUs.
    initializer : callable, optional
        If specified, a callable that will be invoked by each worker process
        when it starts.
    initargs : iterable, optional
        Arguments for ``initializer``; it will be called as
        ``initializer(*initargs)``.
    kwargs:
        Extra arguments passed to the :class:`multiprocess.pool.Pool` superclass.

    """

    wait_timeout = 3600

    def __init__(self, processes=None, initializer=None, initargs=(), **kwargs):
        new_initializer = functools.partial(_initializer_wrapper, initializer)
        super().__init__(processes, new_initializer, initargs, **kwargs)
        self.size = self._processes

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
        results : list
            A list of results from the output of each ``worker()`` call.

        """

        callbackwrapper = CallbackWrapper(callback) if callback is not None else None

        # The key magic is that we must call r.get() with a timeout, because
        # a Condition.wait() without a timeout swallows KeyboardInterrupts.
        r = self.map_async(
            func, iterable, chunksize=chunksize, callback=callbackwrapper
        )

        while True:
            try:
                return r.get(self.wait_timeout)

            except multiprocess.TimeoutError:
                pass

            except KeyboardInterrupt:
                self.terminate()
                self.join()
                raise
