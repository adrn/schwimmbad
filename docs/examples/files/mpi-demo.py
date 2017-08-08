def worker(task):
    a, b = task
    return a**2 + b**2

def main(pool):
    # Here we generate some fake data
    import random
    a = [random.random() for _ in range(10000)]
    b = [random.random() for _ in range(10000)]

    tasks = list(zip(a, b))
    results = pool.map(worker, tasks)
    pool.close()

    print(results[:8])

if __name__ == "__main__":
    import sys
    from schwimmbad import MPIPool

    pool = MPIPool()

    if not pool.is_master():
        pool.wait()
        sys.exit(0)

    main(pool)
