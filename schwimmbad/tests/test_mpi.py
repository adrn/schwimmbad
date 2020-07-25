"""
I couldn't figure out how to get py.test and MPI to play nice together,
so this is a script that tests the MPIPool
"""

# Standard library
import os
import random

import pytest

# Use full imports so we can run this with mpiexec externally
from schwimmbad.tests import TEST_MPI  # noqa
from schwimmbad.tests.test_pools import _function, _batch_function, isclose
from schwimmbad.mpi import MPIPool, MPI, MPIAsyncPool  # noqa


def _callback(x):
    pass


@pytest.mark.skip(True, reason="tested outside of standard pytest call")
def test_mpi():
    with MPIPool() as pool:
        all_tasks = [[random.random() for i in range(1000)]]

        # test map alone
        for tasks in all_tasks:
            results = pool.map(_function, tasks)
            for r1, r2 in zip(results, [_function(x) for x in tasks]):
                assert isclose(r1, r2)

                assert len(results) == len(tasks)

        # test map with callback
        for tasks in all_tasks:
            results = pool.map(_function, tasks, callback=_callback)
            for r1, r2 in zip(results, [_function(x) for x in tasks]):
                assert isclose(r1, r2)

                assert len(results) == len(tasks)



@pytest.mark.skip(True, reason="tested outside of standard pytest call")
def test_mpi_async():
    all_tasks = [[random.random() for i in range(1000)]]

    with MPIAsyncPool() as pool:

        # test map alone
        for tasks in all_tasks:
            results = pool.map(_function, tasks)
            for r1, r2 in zip(results, [_function(x) for x in tasks]):
                assert isclose(r1, r2)

            assert len([r for r in pool.map(_function, tasks)]) == len(tasks)

        # test map with callback
        for tasks in all_tasks:
            results = pool.map(_function, tasks, callback=_callback)
            for r1, r2 in zip(results, [_function(x) for x in tasks]):
                assert isclose(r1, r2)

            assert len([r for r in pool.map(_function, tasks)]) == len(tasks)

        # test batched map
        results = pool.batched_map(_batch_function, tasks)
        for r in results:
            assert all([isclose(x, 42.01) for x in r])


if __name__ == '__main__':
    if 'SCHWIMMBAD_TEST_MPI' in os.environ:
        test_mpi()

    if 'SCHWIMMBAD_TEST_MPIASYNC' in os.environ:
        test_mpi_async()
