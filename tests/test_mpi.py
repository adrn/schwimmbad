# type: ignore
"""
I couldn't figure out how to get py.test and MPI to play nice together,
so this is a script that tests the MPIPool
"""

# Standard library
import random

from schwimmbad._test_helpers import _batch_function, _function, isclose


def _callback(x):
    pass


def test_mpi(pool):
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

    # test batched map
    results = pool.batched_map(_batch_function, tasks)
    for r in results:
        assert all([isclose(x, 42.01) for x in r])

    print("All tests passed")


if __name__ == "__main__":
    from schwimmbad.mpi import MPIPool

    with MPIPool() as pool:
        test_mpi(pool)
