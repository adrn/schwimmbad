
********************************************
Selecting a pool with command-line arguments
********************************************

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
:class:`~schwimmbad.serial.SerialPool`), (2) pass ``--ncores`` with an integer
to specify the number of cores to run using Python's :mod:`multiprocessing`
utilities (with the :class:`~schwimmbad.multiprocessing.MultiPool`), or (3)
pass ``--mpi`` by itself to specify that we'd like to run with MPI (with the
:class:`~schwimmbad.mpi.MPIPool`)::

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
