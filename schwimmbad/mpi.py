# Standard library
from __future__ import division, print_function, absolute_import, unicode_literals

# On some systems mpi4py is available but broken we avoid crashes by importing
# it only when an MPI Pool is explicitly created.
# Still make it a global to avoid messing up other things.
MPI = None

# Project
from . import log, _VERBOSE
from .pool import BasePool

def _dummy_callback(x):
    pass

def _import_mpi(quiet=False):
    global MPI
    try:
        import mpi4py.MPI
        MPI = mpi4py.MPI
    except ImportError:
        if not quiet:
            # Re-raise with a more user-friendly error:
            raise ImportError("Please install mpi4py")

class MPIPool(BasePool):
    """
    This implementation is based on the code here:
    https://github.com/juliohm/HUM/blob/master/pyhum/utils.py#L24
    """

    def __init__(self, comm=None):
        _import_mpi()

        if comm is None:
            comm = MPI.COMM_WORLD
        self.comm = comm

        self.master = 0
        self.rank = self.comm.Get_rank()
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
        """
        Make the workers listen to the master.
        """
        if self.is_master():
            return

        worker = self.comm.rank
        status = MPI.Status()
        while True:
            log.log(_VERBOSE, "Worker {0} waiting for task".format(worker))

            task = self.comm.recv(source=self.master, tag=MPI.ANY_TAG, status=status)

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

    def map(self, func, iterable, callback=None):
        """
        Evaluate a function at various points in parallel. Results are
        returned in the requested order (i.e. y[i] = f(x[i])).
        """

        # If not the master just wait for instructions.
        if not self.is_master():
            self.wait()
            return

        if callback is None:
            callback = _dummy_callback

        workerset = self.workers.copy()
        tasklist = [(tid, (func, arg)) for tid, arg in enumerate(iterable)]
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
            result = self.comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
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
        """
        Tell all the workers to quit work.
        """
        if self.is_worker():
            return

        for worker in self.workers:
            self.comm.send(None, worker, 0)
