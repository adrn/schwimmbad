"""
I couldn't figure out how to get py.test and MPI to play nice together, 
so this is a script that tests the MPIPool
"""

# Standard library
import random
import sys

# Project
from schwimmbad.mpi import MPIPool, MPI
from schwimmbad.tests.test_pools import isclose, _function

def callback(x):
    assert MPI.COMM_WORLD.Get_rank() == 0

if MPI is not None and MPI.COMM_WORLD.Get_size() > 1:

    pool = MPIPool()

    if not pool.is_master():
        pool.wait()
        sys.exit(0)
    
    all_tasks = [[random.random() for i in range(1000)]]
    
    # test map alone
    for tasks in all_tasks:
        results = pool.map(_function, tasks)
        for r1,r2 in zip(results, [_function(x) for x in tasks]):
            assert isclose(r1, r2)

    # test map with callback
    for tasks in all_tasks:
        results = pool.map(_function, tasks, callback=callback)
        for r1,r2 in zip(results, [_function(x) for x in tasks]):
            assert isclose(r1, r2)

    pool.close()
