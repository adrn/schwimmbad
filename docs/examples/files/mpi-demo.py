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

    print(f"computed {len(results)} results, here is a sample")
    print(results[:8])


if __name__ == "__main__":
    from schwimmbad import MPIPool

    with MPIPool() as pool:
        main(pool)
