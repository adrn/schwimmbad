# type: ignore
from typing import Any, Union

from ._version import version as __version__
from .jl import JoblibPool
from .mpi import MPIPool
from .multiprocessing import MultiPool
from .serial import SerialPool


def choose_pool(
    mpi: bool = False, processes: int = 1, **kwargs: Any
) -> Union[MPIPool, MultiPool, SerialPool]:
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
            msg = "Tried to run with MPI but MPIPool not enabled."
            raise SystemError(msg)

        return MPIPool(**kwargs)

    if processes != 1 and MultiPool.enabled():
        return MultiPool(processes=processes, **kwargs)

    return SerialPool(**kwargs)


__all__ = [
    "__version__",
    "choose_pool",
    "JoblibPool",
    "MPIPool",
    "MultiPool",
    "SerialPool",
    "choose_pool",
]
