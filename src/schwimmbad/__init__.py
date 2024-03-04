# coding: utf-8
"""
Contributions by:
- Peter K. G. Williams
- Júlio Hoffimann Mendes
- Dan Foreman-Mackey

Implementations of four different types of processing pools:

    - MPIPool: An MPI pool.
    - MultiPool: A multiprocessing for local parallelization.
    - SerialPool: A serial pool, which uses the built-in ``map`` function

"""
import pkg_resources

__version__ = pkg_resources.require(__package__)[0].version
__author__ = "Adrian Price-Whelan <adrianmpw@gmail.com>"

# Standard library
import sys
import logging
log = logging.getLogger(__name__)
_VERBOSE = 5

from .multiprocessing import MultiPool
from .serial import SerialPool
from .mpi import MPIPool
from .jl import JoblibPool

def choose_pool(mpi=False, processes=1, **kwargs):
    """
    Choose between the different pools given options from, e.g., argparse.

    Parameters
    ----------
    mpi : bool, optional
        Use the MPI processing pool, :class:`~schwimmbad.mpi.MPIPool`. By
        default, ``False``, will use the :class:`~schwimmbad.serial.SerialPool`.
    processes : int, optional
        Use the multiprocessing pool,
        :class:`~schwimmbad.multiprocessing.MultiPool`, with this number of
        processes. By default, ``processes=1``, will use the
        :class:`~schwimmbad.serial.SerialPool`.
    **kwargs
        Any additional kwargs are passed in to the pool class initializer
        selected by the arguments.
    """

    if mpi:
        if not MPIPool.enabled():
            raise SystemError("Tried to run with MPI but MPIPool not enabled.")

        pool = MPIPool(**kwargs)
        log.info("Running with MPI on {0} cores".format(pool.size))
        return pool

    elif processes != 1 and MultiPool.enabled():
        log.info("Running with MultiPool on {0} cores".format(processes))
        return MultiPool(processes=processes, **kwargs)

    else:
        log.info("Running with SerialPool")
        return SerialPool(**kwargs)
