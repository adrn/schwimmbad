import math


def worker(task):
    a, b = task
    return math.cos(a) + math.sin(b)


def main(pool):
    # Here we generate some fake data
    import random
    a = [random.uniform(0, 2*math.pi) for _ in range(10000)]
    b = [random.uniform(0, 2*math.pi) for _ in range(10000)]

    tasks = list(zip(a, b))
    results = pool.map(worker, tasks)

    # Now we could save or do something with the results object


if __name__ == "__main__":
    import schwimmbad

    from argparse import ArgumentParser
    parser = ArgumentParser(description="Schwimmbad example.")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--ncores", dest="n_cores", default=1,
                       type=int, help="Number of processes (uses "
                                      "multiprocessing).")
    group.add_argument("--mpi", dest="mpi", default=False,
                       action="store_true", help="Run with MPI.")
    args = parser.parse_args()

    pool = schwimmbad.choose_pool(mpi=args.mpi, processes=args.n_cores)
    main(pool)
    pool.close()
