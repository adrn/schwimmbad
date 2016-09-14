# Standard library
from __future__ import division, print_function, absolute_import, unicode_literals
import time
import sys
import random

# Third-party
import pytest

# Project
from ..error import PoolError
from ..serial import SerialPool
from ..multiprocessing import MultiPool
try:
    from ..mpi import MPIPool, MPIPool2
    HAS_MPI = True
except:
    HAS_MPI = False

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
            results = pool.map(_function, tasks, callback=callback)
            for r1,r2 in zip(results, [_function(x) for x in tasks]):
                assert isclose(r1, r2)

        pool.close()

class TestSerialPool(PoolTestBase):
    def setup(self):
        self.PoolClass = SerialPool

    def test_wait_fail(self):
        pool = self.PoolClass()
        with pytest.raises(PoolError):
            pool.wait()

class TestMultiPool(PoolTestBase):
    def setup(self):
        self.PoolClass = MultiPool

@pytest.mark.skipif(not HAS_MPI,
                    reason="Doesn't have MPI.")
class TestMPIPool(PoolTestBase):

    def setup(self):
        self.PoolClass = MPIPool

    def _make_pool(self):
        pool = self.PoolClass()

        if not pool.is_master():
            pool.wait()
            sys.exit(0)

        return pool
