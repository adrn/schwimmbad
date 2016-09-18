# Standard library
from __future__ import division, print_function, absolute_import, unicode_literals
import time
import random

# Project
from ..serial import SerialPool
from ..multiprocessing import MultiPool
from ..jl import JoblibPool
try:
    from mpi4py import MPI
except ImportError:
    MPI = None

def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

def _function(x):
    """
    Wastes a random amount of time, returns the number 42.01
    """
    time.sleep(random.random()*4E-4 + 1E-4)
    return 42.01

def callback(x):
    assert isclose(x, 42.01)

class PoolTestBase(object):

    all_tasks = [[random.random() for i in range(1000)]]

    def test_init_close(self):
        pool = self.PoolClass()
        pool.close()

    def _make_pool(self):
        return self.PoolClass()

    def test_map(self):
        pool = self._make_pool()

        for tasks in self.all_tasks:
            results = pool.map(_function, tasks)
            for r1,r2 in zip(results, [_function(x) for x in tasks]):
                assert isclose(r1, r2)

        pool.close()

    def test_map_callback(self):
        pool = self._make_pool()

        for tasks in self.all_tasks:

            mylist = []
            def _callback(o):
                mylist.append(o)

            results = pool.map(_function, tasks, callback=_callback)
            for r1,r2 in zip(results, [_function(x) for x in tasks]):
                assert isclose(r1, r2)
            assert len(mylist) == len(tasks)

        pool.close()

class TestSerialPool(PoolTestBase):
    def setup(self):
        self.PoolClass = SerialPool

class TestMultiPool(PoolTestBase):
    def setup(self):
        self.PoolClass = MultiPool

class TestJoblibPool(PoolTestBase):
    def setup(self):
        self.PoolClass = JoblibPool
