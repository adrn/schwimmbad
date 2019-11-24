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


def main(pool):
    worker = Worker('output_file.txt')

    tasks = list(zip(range(16384), range(16384)[::-1]))

    for r in pool.map(worker, tasks, callback=worker.callback):
        pass


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
    pool.close()
