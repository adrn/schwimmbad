"""
Contributions by:
- Rodrigo Luger
- Joe Zuntz
- Peter K. G. Williams
- Júlio Hoffimann Mendes

Implementations of four different types of processing pools:

    - MPIPool: An MPI pool borrowed from ``emcee``. This pool passes Python
      objects back and forth to the workers and communicates once per task.

    - MPIOptimizedPool: An attempt at an optimized version of the MPI pool,
      specifically for passing arrays of numpy floats. If the length of the
      array passed to the ``map`` method is larger than the number of processes,
      the iterable is passed in chunks, which are processed *serially* on each
      processor. This minimizes back-and-forth communication and should increase
      the speed a bit.

    - MultiPool: A multiprocessing for local parallelization, borrowed from
      ``emcee``

    - SerialPool: A serial pool, which uses the built-in ``map`` function

"""

# Standard library
import sys
import logging
log = logging.getLogger(__name__)
VERBOSE = 5

def choose_pool(mpi=False, processes=1, **kwargs):
    """
    Chooses between the different pools.
    """
    from .multiprocessing import MultiPool
    from .serial import SerialPool

    if mpi:
        from .mpi import MPIPool2
        if not MPIPool2.enabled():
            raise ValueError("MPI not enables. Did you run with mpirun or the equivalent?")

        pool = MPIPool2(**kwargs)
        if not pool.is_master():
            sys.exit(0)

        log.info("Running with MPI")
        return pool

    elif processes > 1 and MultiPool.enabled():
        log.info("Running with multiprocessing on {} cores".format(processes))
        return MultiPool(processes=processes, **kwargs)

    else:
        log.info("Running serial")
        return SerialPool(**kwargs)
