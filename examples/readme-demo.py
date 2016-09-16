"""
After installing `schwimmbad`, try running this script as:

    python readme-demo.py

    # if you have >1 CPUs
    python readme-demo.py --ncores=2

    # if you have an implementation of MPI + mpi4py installed
    mpiexec -n 2 python readme-demo.py --mpi

"""
from schwimmbad import choose_pool

def worker(task):
    # do something with the task!
    return task**2

def main(pool):
    tasks = range(10000)
    results = pool.map(worker, tasks)
    pool.close()

    print("Received {} results".format(len(results)))

if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser(description="")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--ncores", dest="n_cores", default=1,
                       type=int, help="Number of processes (uses multiprocessing).")
    group.add_argument("--mpi", dest="mpi", default=False,
                       action="store_true", help="Run with MPI.")
    args = parser.parse_args()

    pool = choose_pool(mpi=args.mpi, processes=args.n_cores)
    main(pool)
