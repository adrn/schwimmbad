try:
    from joblib import Parallel, delayed
except ImportError:
    Parallel = None

from .pool import BasePool

__all__ = ["JoblibPool"]

class JoblibPool(BasePool):
    """A processing pool that distributes tasks using ``joblib.Parallel``.

    This pool processes parallel tasks using the ``Parallel`` module of the
    `joblib <https://pythonhosted.org/joblib>`_ library. All arguments and
    keyword arguments are passed directly to the ``__init__`` method of the
    `Parallel object provided by joblib
    <https://pythonhosted.org/joblib/parallel.html#parallel-reference-documentation>`_.

    """

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
