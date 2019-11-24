.. module:: schwimmbad

********
Examples
********

Using MPIPool
=============

To see an example, download, read, and execute
:download:`the provided demo file <files/mpi-demo.py>` on just 2 processes (the
master process and 1 worker) using:

.. code-block:: bash

    mpiexec -n 2 python mpi-demo.py

Using JoblibPool
================

:class:`schwimmbad.JoblibPool` is a pool built using the `Parallel
capabilities <https://pythonhosted.org/joblib/parallel.html>`_ of the `joblib
<https://pythonhosted.org/joblib/>`_ module. To use this pool, first `install
joblib <https://pythonhosted.org/joblib/installing.html>`_. Then use it like
any other pool:

.. code-block:: python

    from schwimmbad import JoblibPool

    with JoblibPool(4) as pool:
        pool.map(expensive_code, iterator)

One benefit of the :class:`JoblibPool` is that it provides a ``threading``
back end that can be used to parallelize tasks that release the GIL without
increasing the memory usage. If you have code that explicitly releases the GIL
(using the ``with nogil`` Cython command, for example) you can parallelize it
using the :class:`JoblibPool` as follows:

.. code-block:: python

    with JoblibPool(4, backend="threading") as pool:
        pool.map(nogil_code, iterator)

Using MultiPool (with ``emcee``)
================================

The :class:`emcee.EnsembleSampler` class in `emcee
<http://emcee.readthedocs.io/en/stable/>`_ supports ``multiprocessing`` in two
ways: either with the ``n_threads`` keyword argument, or by specifying your own
pool class. This can be any of the pool classes mentioned above, but as an
example of this we'll use the :class:`MultiPool` class implemented in
schwimmbad.

To use ``emcee``, we'll need to define a probability function to sample from.
For this demo, we'll just use a Gaussian with mean ``mean`` and variance
``var`` specified as arguments to the (log-)probability function:

.. code-block:: python

    from schwimmbad import MultiPool
    import emcee
    import matplotlib.pyplot as plt

    def ln_probability(p, mean, var):
        x = p[0]
        return -0.5 * (x-mean)**2 / var

    # initial positions for the walkers
    n_walkers = 16
    p0 = np.random.uniform(0, 10, (n_walkers, 1))

    with MultiPool() as pool:
        sampler = emcee.EnsembleSampler(n_walkers, dim=1,
                                        lnpostfn=ln_probability,
                                        args=(5, 1.2),
                                        pool=pool) # the important line

        pos,_,_ = sampler.run_mcmc(p0, 500)
        sampler.reset()
        sampler.run_mcmc(p0, 1000)

    plt.figure()
    plt.hist(sampler.flatchain)

.. plot::
    :align: center

    from schwimmbad import MultiPool
    import emcee
    import matplotlib.pyplot as plt

    def ln_probability(p, mean, var):
        x = p[0]
        return -0.5 * (x-mean)**2 / var

    # initial positions for the walkers
    n_walkers = 16
    p0 = np.random.uniform(0, 10, (n_walkers, 1))

    sampler = emcee.EnsembleSampler(n_walkers, dim=1, lnpostfn=ln_probability,
                                    args=(5, 1.2))

    pos,_,_ = sampler.run_mcmc(p0, 500)
    sampler.reset()
    sampler.run_mcmc(p0, 1000)

    plt.figure()
    plt.hist(sampler.flatchain)

.. _select-pool-command-line:

Selecting a pool with command-line arguments
============================================

``schwimmbad`` is particularly useful for writing code that can be executed in
multiple parallel processing environments without having to edit the code
directly. This is because once a ``pool`` object is created, the subsequent
processing code can be agnostic to the particular mode of processing. For
example (a use-case from astronomy), imagine that we need to perform some type
of parameter fitting or optimization for a large number of objects and store the
results. We have many objects, so we ultimately want to deploy this script onto
a compute cluster where the work can be spread over multiple nodes on the
cluster. But, when developing and debugging the script, we want to be able to
execute the script locally both in serial-processing mode and perhaps also with
:mod:`multiprocessing` to test any parallel functionality. Here's a
demonstration of such a use case. The code below is meant to be added to a
Python script/module; the full example can be :download:`downloaded here
<files/script-demo.py>`.

We start by defining a "worker" function: this is the function that will take a
single "task" (e.g., one datum or one object's data) and returns a result based
on that task. For this example, we'll simply evaluate some trigonometric
functions on two values passed in with the "task." Note that the worker function
has to take a single argument (the task), but that can be an iterable::

    import math

    def worker(task):
        a, b = task
        return math.cos(a) + math.sin(b)

We next define a ``main()`` function that accepts a ``pool`` object and performs
the actual processing::

    def main(pool):
        # Here we generate some fake data
        import random
        a = [random.uniform(0, 2*math.pi) for _ in range(10000)]
        b = [random.uniform(0, 2*math.pi) for _ in range(10000)]

        tasks = list(zip(a, b))
        results = pool.map(worker, tasks)
        pool.close()

        # Now we could save or do something with the results object

With a few extra lines of code using Python's :mod:`argparse` module, we can add
command-line flags to the script that allow us to choose the processing method
when we run the script. With the specified arguments below, we can either (1)
pass no flags, in which case the script is run in serial (with the
:class:`~schwimmbad.SerialPool`), (2) pass ``--ncores`` with an integer to
specify the number of cores to run using Python's :mod:`multiprocessing`
utilities (with the :class:`~schwimmbad.MultiPool`), or (3) pass ``--mpi`` by
itself to specify that we'd like to run with MPI (with the
:class:`~schwimmbad.MPIPool`)::

    if __name__ == "__main__":
        import schwimmbad

        from argparse import ArgumentParser
        parser = ArgumentParser(description="Schwimmbad example.")

        group = parser.add_mutually_exclusive_group()
        group.add_argument("--ncores", dest="n_cores", default=1,
                           type=int, help="Number of processes (uses multiprocessing).")
        group.add_argument("--mpi", dest="mpi", default=False,
                           action="store_true", help="Run with MPI.")
        args = parser.parse_args()

        pool = schwimmbad.choose_pool(mpi=args.mpi, processes=args.n_cores)
        main(pool)

Note that for the first two options, we can run the script as usual using,
e.g.

.. code-block:: bash

    python script-demo.py

or

.. code-block:: bash

    python script-demo.py --ncores=4

To run with MPI, we have to use the compiled MPI executable, which depends on
the environment and MPI installation you are using. For example, for OpenMPI, by
default this is likely ``mpiexec``:

.. code-block:: bash

    mpiexec -n 4 python script-demo.py --mpi

This full example can be :download:`downloaded here <files/script-demo.py>`.


Advanced usage: a class-based worker and callback functions
===========================================================

This example will demonstrate two more advanced but common use-cases for
parallel processing: (1) the need to write output to a file in a safe way,
i.e. so that processes aren't trying to write to the file at the same time, and
(2) the need to pass some configuration settings or parameters to the worker
function each time it is run.

To satisfy both of these needs, we're going to create a class to act as our
worker (instead of a function), and allow the objects instantiaed from this
class to be called like a function by defining the ``__call__`` method. The
arguments of the class initializer will allow us to set global parameters for
all workers. We'll then also define a callback function as a method of the class
to handle writing output to a file (only ever from the master process). Let's
consider a simple example: we need to pass a file path in to each walker, and we
need to write to that file each time a result is computed from the worker. Let's
define a class that accepts a path to the output file, a method that actually
does some work (in this case, just computes a simple quantity based on the task
passed in), and defines a callback function that appends each result to the
specified output file::

    import schwimmbad

    class Worker(object):

        def __init__(self, output_path):
            self.output_path = output_path

        def work(self, a, b):
            # For example, all we do is compute a third value
            c = 2*a*b - b**2
            return c

        def callback(self, result):
            with open(self.output_path, 'a') as f:
                f.write("{0}\n".format(result))

        def __call__(self, task):
            a, b = task
            return self.work(a, b)

We can now follow a similar paradigm to that used in
:ref:`select-pool-command-line`::

    def main(pool):
        worker = Worker('output_file.txt')

        tasks = list(zip(range(16384), range(16384)[::-1]))

        for r in pool.map(worker, tasks, callback=worker.callback):
            pass

        pool.close()

    if __name__ == "__main__":
        from argparse import ArgumentParser
        parser = ArgumentParser(description="")

        group = parser.add_mutually_exclusive_group()
        group.add_argument("--ncores", dest="n_cores", default=1,
                           type=int, help="Number of processes (uses multiprocessing).")
        group.add_argument("--mpi", dest="mpi", default=False,
                           action="store_true", help="Run with MPI.")
        args = parser.parse_args()

        pool = schwimmbad.choose_pool(mpi=args.mpi, processes=args.n_cores)
        main(pool)
