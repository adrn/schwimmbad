"""
I couldn't figure out how to get py.test and MPI to play nice together,
so this is a script that tests the MPIPool
"""

# Standard library
import random

import pytest

# Use full imports so we can run this with mpiexec externally
from schwimmbad.tests import TEST_MPI  # noqa
from schwimmbad.mpi import MPIPool, MPI  # noqa


def worker_error(task):
    raise AttributeError("Derp")


@pytest.mark.skip(True, reason="WTF")
def test_mpi_worker_error():
    with MPIPool() as pool:
        tasks = [random.random() for i in range(1000)]
        pool.map(worker_error, tasks)  # should fail


if __name__ == '__main__':
    test_mpi_worker_error()
