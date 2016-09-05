# Standard library
from __future__ import division, print_function, absolute_import, unicode_literals

# Third-party
from mpi4py import MPI
import numpy as np

# Project
from . import log, VERBOSE
from .pool import BasePool

# Tags and messages
TAG_TASK = 0
TAG_NEW_FUNC = 1
TAG_NEW_DIMS = 2
TAG_CLOSE = 3
MSG_EMPTY = lambda: np.empty(1, dtype='float64')

class _close_pool_message(object):
    def __repr__(self):
        return "<Close pool message>"

class _function_wrapper(object):
    def __init__(self, function):
        self.function = function

def _placeholder_function(*args):
    """
    The placeholder worker function. Should be replaced
    with the desired mapping function on the first
    call.
    """
    raise Exception("Pool was sent tasks before being told what function to apply.")

class MPIPool(BasePool):
    """
    A pool that distributes tasks over a set of MPI processes. MPI is an API for
    distributed memory parallelism.  This pool will let you run processes
    without shared memory, letting you use much larger machines.

    The pool only supports the :func:`map` method at the moment. That being
    said, this pool is fairly general and it could be used for other purposes.

    :param comm: (optional)
        The ``mpi4py`` communicator.

    :param loadbalance: (optional)
        if ``True`` and ntask > Ncpus, tries to loadbalance by sending
        out one task to each cpu first and then sending out the rest
        as the cpus get done.
    """
    def __init__(self, comm=None, loadbalance=True,
                 wait_on_start=True, exit_on_end=True, **kwargs):

        self.comm = MPI.COMM_WORLD if comm is None else comm
        self.rank = self.comm.Get_rank()
        self.size = self.comm.Get_size() - 1
        self.function = _placeholder_function
        self.loadbalance = loadbalance

        if self.size == 0:
            raise ValueError("Tried to create an MPI pool, but there "
                             "was only one MPI process available. "
                             "Need at least two.")

        self.exit_on_end = exit_on_end

        # Enter main loop for workers?
        if wait_on_start:
            if self.is_worker():
                self.wait()

    @staticmethod
    def enabled():
        if MPI is not None:
            if MPI.COMM_WORLD.size > 1:
                return True
        return False

    def wait(self):
        """ If this isn't the master process, wait for instructions. """

        if self.is_master():
            raise RuntimeError("Master node told to await jobs.")

        status = MPI.Status()

        # The main event loop:
        while True:
            # Sit and await instructions
            log.log(VERBOSE, "Worker {0} waiting for task.".format(self.rank))

            # Blocking receive to wait for instructions.
            task = self.comm.recv(source=0, tag=MPI.ANY_TAG, status=status)

            log.log(VERBOSE, "Worker {0} got task {1} with tag {2}."
                    .format(self.rank, type(task), status.tag))

            # Check if message is special sentinel signaling end; if so, stop
            if isinstance(task, _close_pool_message):
                log.log(VERBOSE, "Worker {0} told to quit.".format(self.rank))
                break

            # Check if message is special type containing new function
            #   to be applied
            if isinstance(task, _function_wrapper):
                self.function = task.function
                log.log(VERBOSE, "Worker {0} replaced its task function: {1}."
                        .format(self.rank, self.function))
                continue

            # If not a special message, just run the known function on
            #   the input and return it asynchronously.
            result = self.function(task)
            log.log(VERBOSE, "Worker {0} sending answer {1} with tag {2}."
                    .format(self.rank, type(result), status.tag))
            self.comm.isend(result, dest=0, tag=status.tag) # send to master

        # kill the process if exit on end
        if self.exit_on_end:
            sys.exit(0)

    def map(self, function, tasks):
        """
        Like the built-in :func:`map` function, apply a function to all
        of the values in a list and return the list of results.

        :param function:
            The function to apply to the list.

        :param tasks:
            The list of elements.

        """
        n_tasks = len(tasks)

        # If not the master just wait for instructions.
        if not self.is_master():
            self.wait()
            return

        # Replace the function to apply with the input
        if function is not self.function:
            log.log(VERBOSE, "Master replacing pool function with {0}."
                    .format(function))

            self.function = function
            F = _function_wrapper(function)

            # Tell all the workers what function to use.
            requests = []
            for i in range(self.size):
                r = self.comm.isend(F, dest=i + 1)
                requests.append(r)

            # Wait until all of the workers have responded. See:
            #       https://gist.github.com/4176241
            MPI.Request.waitall(requests)

        if (not self.loadbalance) or (n_tasks <= self.size):

            # Send all the tasks off and wait for them to be received:
            requests = []
            for i, task in enumerate(tasks):
                worker = i % self.size + 1
                log.log(VERBOSE, "Sent task {0} to worker {1} with tag {2}."
                        .format(type(task), worker, i))
                r = self.comm.isend(task, dest=worker, tag=i)
                requests.append(r)

            MPI.Request.waitall(requests)

            # Receive the responses:
            results = []
            for i in range(n_tasks):
                worker = i % self.size + 1
                log.log(VERBOSE, "Master waiting for worker {0} with tag {1}"
                        .format(worker, i))
                result = self.comm.recv(source=worker, tag=i)

                results.append(result)

            return results

        else:

            # Perform load-balancing. The order of the results are likely to
            #   be different from the case with no load-balancing
            for i, task in enumerate(tasks[0:self.size]):
                worker = i+1
                log.log(VERBOSE, "Sent task {0} to worker {1} with tag {2}."
                        .format(type(task), worker, i))

                # Send out the tasks asynchronously.
                self.comm.isend(task, dest=worker, tag=i)

            ntasks_dispatched = self.size
            results = [None]*n_tasks
            for itask in range(n_tasks):
                status = MPI.Status()

                # Receive input from workers.
                try:
                    result = self.comm.recv(source=MPI.ANY_SOURCE,
                                            tag=MPI.ANY_TAG, status=status)
                except Exception as e:
                    self.close()
                    raise e

                worker = status.source
                i = status.tag
                results[i] = result

                log.log(VERBOSE, "Master received from worker {0} with tag {1}"
                        .format(worker, i))

                # Send the next task to this idle worker (if there are any left)
                if ntasks_dispatched < n_tasks:
                    task = tasks[ntasks_dispatched]
                    i = ntasks_dispatched
                    log.log(VERBOSE, "Sent task {0} to worker {1} with tag {2}."
                            .format(type(task), worker, i))

                    # Send out the tasks asynchronously.
                    self.comm.isend(task, dest=worker, tag=i)
                    ntasks_dispatched += 1

            return results

    def bcast(self, *args, **kwargs):
        """
        Equivalent to mpi4py :func:`bcast` collective operation.
        """
        return self.comm.bcast(*args, **kwargs)

    def close(self):
        """
        Just send a message off to all the pool members which contains
        the special :class:`_close_pool_message` sentinel.

        """
        if self.is_master():
            for i in range(self.size):
                self.comm.isend(_close_pool_message(), dest=i + 1)

class MPIPool2(BasePool):
    """
    This implementation is based on the code here:
    https://github.com/juliohm/HUM/blob/master/pyhum/utils.py#L24
    """

    def __init__(self, comm=None, wait_on_start=True):

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

        # Enter main loop for workers?
        if wait_on_start:
            if self.is_worker():
                self.wait()

    def wait(self):
        """
        Make the workers listen to the master.
        """
        if self.is_master():
            return

        worker = self.comm.rank
        status = MPI.Status()
        while True:
            log.log(VERBOSE, "Worker {0} waiting for task".format(worker))

            task = self.comm.recv(source=self.master, tag=MPI.ANY_TAG, status=status)

            if task is None:
                log.log(VERBOSE, "Worker {0} told to quit work".format(worker))
                break

            func, arg = task
            log.log(VERBOSE, "Worker {0} got task {1} with tag {2}"
                    .format(worker, arg, status.tag))

            result = func(arg)

            log.log(VERBOSE, "Worker {0} sending answer {1} with tag {2}"
                    .format(worker, result, status.tag))

            self.comm.ssend(result, self.master, status.tag)

    def map(self, func, iterable):
        """
        Evaluate a function at various points in parallel. Results are
        returned in the requested order (i.e. y[i] = f(x[i])).
        """

        # If not the master just wait for instructions.
        if not self.is_master():
            self.wait()
            return

        workerset = self.workers.copy()
        tasklist = [(tid, (func, arg)) for tid, arg in enumerate(iterable)]
        resultlist = [None] * len(tasklist)
        pending = len(tasklist)

        while pending:
            if workerset and tasklist:
                worker = workerset.pop()
                taskid, task = tasklist.pop()
                log.log(VERBOSE, "Sent task {0} to worker {1} with tag {2}"
                        .format(task[1], worker, taskid))
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
            log.log(VERBOSE, "Master received from worker {0} with tag {1}"
                    .format(worker, taskid))

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
