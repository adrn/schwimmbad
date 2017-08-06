
***********************************************************
Advanced usage: a class-based worker and callback functions
***********************************************************

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
