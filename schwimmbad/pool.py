# Standard library
from __future__ import division, print_function, absolute_import, unicode_literals
import abc

# Third-party
import six

__all__ = ['BasePool']

@six.add_metaclass(abc.ABCMeta)
class BasePool(object):
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

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
