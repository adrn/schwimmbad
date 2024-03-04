# Standard library
import abc

# This package
from .utils import batch_tasks

__all__ = ['BasePool']


def _callback_wrapper(callback, generator):
    for element in generator:
        callback(element)
        yield element


class BasePool(metaclass=abc.ABCMeta):
    """ A base class multiprocessing pool with a ``map`` method. """

    def __init__(self, **kwargs):
        self.rank = 0

    @staticmethod
    def enabled():
        return False

    def is_master(self):
        return self.rank == 0

    def is_worker(self):
        return self.rank != 0

    def wait(self):
        return

    @abc.abstractmethod
    def map(self, *args, **kwargs):
        return

    def batched_map(self, worker, tasks, *args, **kwargs):
        batches = batch_tasks(n_batches=self.size, arr=tasks)
        return self.map(worker, batches, *args, **kwargs)

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def _call_callback(self, callback, generator):
        if callback is None:
            return generator
        return _callback_wrapper(callback, generator)
