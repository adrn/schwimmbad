# Standard library
from __future__ import division, print_function, absolute_import, unicode_literals

# Project
from .pool import BasePool
from .error import PoolError

class SerialPool(BasePool):

    def __init__(self, **kwargs):
        self.size = 0
        self.rank = 0

    @staticmethod
    def enabled():
        return True

    def wait(self):
        raise PoolError('SerialPool cannot be told to wait!')

    def map(self, function, iterable):
        return list(map(function, iterable))
