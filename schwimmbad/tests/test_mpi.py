"""
I couldn't figure out how to get py.test and MPI to play nice together,
so this is a script that tests the MPIPool
"""

# Standard library
import random
import sys

import pytest

# Use full imports so we can run this with mpiexec externally
from schwimmbad.tests import TEST_MPI
from schwimmbad.tests.test_pools import _function, isclose
from schwimmbad.mpi import MPIPool, MPI

def _callback(x):
    pass

@pytest.mark.skip(True, reason="WTF")
def test_mpi():
    pool = MPIPool()

    pool.wait(lambda: sys.exit(0))

    all_tasks = [[random.random() for i in range(1000)]]

    # test map alone
    for tasks in all_tasks:
        results = pool.map(_function, tasks)
        for r1,r2 in zip(results, [_function(x) for x in tasks]):
            assert isclose(r1, r2)

        assert len(results) == len(tasks)

    # test map with callback
    for tasks in all_tasks:
        results = pool.map(_function, tasks, callback=_callback)
        for r1,r2 in zip(results, [_function(x) for x in tasks]):
            assert isclose(r1, r2)

        assert len(results) == len(tasks)

    pool.close()

@pytest.mark.skip(True, reason="WTF")
def test_mpi_with_dill():
    with MPIPool(use_dill=True) as pool:
        if not pool.is_master():
            pool.wait()
            sys.exit(0)

        all_tasks = [[random.random() for i in range(1000)]]

        # test map alone
        for tasks in all_tasks:
            results = pool.map(_function, tasks)
            for r1,r2 in zip(results, [_function(x) for x in tasks]):
                assert isclose(r1, r2)

            assert len(results) == len(tasks)

        # test map with callback
        for tasks in all_tasks:
            results = pool.map(_function, tasks, callback=_callback)
            for r1,r2 in zip(results, [_function(x) for x in tasks]):
                assert isclose(r1, r2)

            assert len(results) == len(tasks)


if __name__ == '__main__':
    test_mpi()
    test_mpi_with_dill()
