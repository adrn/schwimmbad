# Standard library
import atexit
import sys
import traceback

# On some systems mpi4py is available but broken we avoid crashes by importing
# it only when an MPI Pool is explicitly created.
# Still make it a global to avoid messing up other things.
MPI = None

# Project
from . import log, _VERBOSE
from .pool import BasePool

__all__ = ['MPIPool']


def _dummy_callback(x):
    pass


def _import_mpi(quiet=False, use_dill=False):
    global MPI
    try:
        from mpi4py import MPI as _MPI
        if use_dill:
            import dill
            _MPI.pickle.__init__(dill.dumps, dill.loads, dill.HIGHEST_PROTOCOL)
        MPI = _MPI
    except ImportError:
        if not quiet:
            # Re-raise with a more user-friendly error:
            raise ImportError("Please install mpi4py")

    return MPI


class MPIPool(BasePool):
    """A processing pool that distributes tasks using MPI.

    With this pool class, the master process distributes tasks to worker
    processes using an MPI communicator. This pool therefore supports parallel
    processing on large compute clusters and in environments with multiple
    nodes or computers that each have many processor cores.

    This implementation is inspired by @juliohm in `this module
    <https://github.com/juliohm/HUM/blob/master/pyhum/utils.py#L24>`_

    Parameters
    ----------
    comm : :class:`mpi4py.MPI.Comm`, optional
        An MPI communicator to distribute tasks with. If ``None``, this uses
        ``MPI.COMM_WORLD`` by default.
    use_dill: Set `True` to use `dill` serialization. Default is `False`.
    """

    def __init__(self, comm=None, use_dill=False):
        MPI = _import_mpi(use_dill=use_dill)

        if comm is None:
            comm = MPI.COMM_WORLD
        self.comm = comm

        self.master = 0
        self.rank = self.comm.Get_rank()

        atexit.register(lambda: MPIPool.close(self))

        if not self.is_master():
            # workers branch here and wait for work
            try:
                self.wait()
            except Exception:
                print(f"worker with rank {self.rank} crashed".center(80, "="))
                traceback.print_exc()
                sys.stdout.flush()
                sys.stderr.flush()
                # shutdown all mpi tasks:
                from mpi4py import MPI
                MPI.COMM_WORLD.Abort()
            finally:
                sys.exit(0)

        self.workers = set(range(self.comm.size))
        self.workers.discard(self.master)
        self.size = self.comm.Get_size() - 1

        if self.size == 0:
            raise ValueError("Tried to create an MPI pool, but there "
                             "was only one MPI process available. "
                             "Need at least two.")

    @staticmethod
    def enabled():
        if MPI is None:
            _import_mpi(quiet=True)
        if MPI is not None:
            if MPI.COMM_WORLD.size > 1:
                return True
        return False

    def wait(self, callback=None):
        """Tell the workers to wait and listen for the master process. This is
        called automatically when using :meth:`MPIPool.map` and doesn't need to
        be called by the user.
        """
        if self.is_master():
            return

        worker = self.comm.rank
        status = MPI.Status()
        while True:
            log.log(_VERBOSE, "Worker {0} waiting for task".format(worker))

            task = self.comm.recv(source=self.master, tag=MPI.ANY_TAG,
                                  status=status)

            if task is None:
                log.log(_VERBOSE, "Worker {0} told to quit work".format(worker))
                break

            func, arg = task
            log.log(_VERBOSE, "Worker {0} got task {1} with tag {2}"
                    .format(worker, arg, status.tag))

            result = func(arg)

            log.log(_VERBOSE, "Worker {0} sending answer {1} with tag {2}"
                    .format(worker, result, status.tag))

            self.comm.ssend(result, self.master, status.tag)

        if callback is not None:
            callback()

    def map(self, worker, tasks, callback=None):
        """Evaluate a function or callable on each task in parallel using MPI.

        The callable, ``worker``, is called on each element of the ``tasks``
        iterable. The results are returned in the expected order (symmetric with
        ``tasks``).

        Parameters
        ----------
        worker : callable
            A function or callable object that is executed on each element of
            the specified ``tasks`` iterable. This object must be picklable
            (i.e. it can't be a function scoped within a function or a
            ``lambda`` function). This should accept a single positional
            argument and return a single object.
        tasks : iterable
            A list or iterable of tasks. Each task can be itself an iterable
            (e.g., tuple) of values or data to pass in to the worker function.
        callback : callable, optional
            An optional callback function (or callable) that is called with the
            result from each worker run and is executed on the master process.
            This is useful for, e.g., saving results to a file, since the
            callback is only called on the master thread.

        Returns
        -------
        results : list
            A list of results from the output of each ``worker()`` call.
        """

        # If not the master just wait for instructions.
        if not self.is_master():
            self.wait()
            return

        if callback is None:
            callback = _dummy_callback

        workerset = self.workers.copy()
        tasklist = [(tid, (worker, arg)) for tid, arg in enumerate(tasks)]
        resultlist = [None] * len(tasklist)
        pending = len(tasklist)

        while pending:
            if workerset and tasklist:
                worker = workerset.pop()
                taskid, task = tasklist.pop()
                log.log(_VERBOSE, "Sent task %s to worker %s with tag %s",
                        task[1], worker, taskid)
                self.comm.send(task, dest=worker, tag=taskid)

            if tasklist:
                flag = self.comm.Iprobe(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG)
                if not flag:
                    continue
            else:
                self.comm.Probe(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG)

            status = MPI.Status()
            result = self.comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG,
                                    status=status)
            worker = status.source
            taskid = status.tag
            log.log(_VERBOSE, "Master received from worker %s with tag %s",
                    worker, taskid)

            callback(result)

            workerset.add(worker)
            resultlist[taskid] = result
            pending -= 1

        return resultlist

    def close(self):
        """ Tell all the workers to quit."""
        if self.is_worker():
            return

        for worker in self.workers:
            self.comm.send(None, worker, 0)
