# Standard library
from __future__ import division, print_function, absolute_import, unicode_literals
import time
import sys

# Third-party
import numpy as np
import pytest

# Project
from .serial import SerialPool
from .multiprocessing import MultiPool
try:
    from .mpi import MPIPool, MPIPool2
    HAS_MPI = True
except:
    HAS_MPI = False

def _function(x):
    """
    Wastes a random amount of time, returns random float
    """
    time.sleep(np.random.uniform(0.001, 0.005))
    return x**2

all_tasks = [np.random.random(size=1000),
             np.random.random(size=(1000,2))]

def test_serial():
    pool = SerialPool()

    for tasks in all_tasks:
        results = pool.map(_function, tasks)
        assert np.allclose(results, [_function(x) for x in tasks])

def test_multi():
    for tasks in all_tasks:
        pool = MultiPool()
        results = pool.map(_function, tasks)
        assert np.allclose(results, [_function(x) for x in tasks])
        pool.close()

@pytest.mark.skipif(not HAS_MPI,
                    reason="Doesn't have MPI.")
def test_mpi():
    for tasks in all_tasks:
        pool = MPIPool()

        if not pool.is_master():
            pool.wait()
            sys.exit(0)

        results = pool.map(_function, tasks)
        pool.close()

        assert np.allclose(results, [_function(x) for x in tasks])
        print(results)
