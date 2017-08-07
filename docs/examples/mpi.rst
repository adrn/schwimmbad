
*************
Using MPIPool
*************

When using the MPI pool, besides instantiating the :class:`schwimmbad.MPIPool`
class, an additional step must be taken to tell all worker processes to wait for
tasks from the master process. This is done with the following:

.. code-block:: python

    pool = MPIPool()

    if not pool.is_master():
        pool.wait()
        sys.exit(0)

To see an example, download, read, and execute
:download:`the provided demo file <files/mpi-demo.py>` on just 2 processes (the
master process and 1 worker) using:

.. code-block:: bash

    mpiexec -n 2 python mpi-demo.py
