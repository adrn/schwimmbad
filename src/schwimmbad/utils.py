# type: ignore
__all__ = ["batch_tasks"]


from .decorators import deprecated_renamed_argument


@deprecated_renamed_argument("arr", "data", since="v0.4")
def batch_tasks(
    n_batches,
    n_tasks=None,
    data=None,
    args=(),
    start_idx=0,
    include_idx=True,
):
    """Split tasks into some number of batches to send out to workers.

    By default, returns index ranges that split the number of tasks into the
    specified number of batches. If an array is passed in via ``data``, it splits
    the array directly along ``axis=0`` into the specified number of batches.

    Parameters
    ----------
    n_batches : int
        The number of batches to split the tasks into. Often, you may want to do
        ``n_batches=pool.size`` for equal sharing amongst MPI workers.
    n_tasks : int (optional)
        The total number of tasks to divide.
    data : iterable, list, array-like (optional)
        Instead of returning indices that specify the batches, you can also
        directly split an array into batches.
    args : iterable (optional)
        Other arguments to add to each task.
    start_idx : int (optional)
        What index in the tasks to start from?
    include_idx : bool (optional)
        If passing an array in, this determines whether to include the indices
        of each batch with each task.
    """
    args = tuple(args)

    if (n_tasks is None and data is None) or (n_tasks is not None and data is not None):
        msg = "you must pass one of n_tasks or data (not both)"
        raise ValueError(msg)

    if data is not None:
        data = list(data)

    # Case where data is None is covered above
    if n_tasks is None and data is not None:
        n_tasks = len(data)

    if n_batches <= 0 or n_tasks <= 0:
        msg = "n_batches and n_tasks must be > 0"
        raise ValueError(msg)

    if n_batches > n_tasks:
        # TODO: add a warning?
        n_batches = n_tasks

    # Chunk by the number of batches, often the pool size
    base_batch_size = n_tasks // n_batches
    rmdr = n_tasks % n_batches

    i1 = start_idx
    indices = []
    for i in range(n_batches):
        i2 = i1 + base_batch_size
        if i < rmdr:
            i2 += 1

        indices.append((i1, i2))
        i1 = i2

    # Add args, possible slice input array:
    tasks = []
    for idx in indices:
        if data is not None and not args and not include_idx:
            tasks.append(data[idx[0] : idx[1]])
            continue

        extra = list()
        if data is not None:
            extra.append(data[idx[0] : idx[1]])
        if args:
            extra.extend(args)

        if extra and include_idx:
            tasks.append(tuple([idx] + extra))
        elif extra and not include_idx:
            tasks.append(extra)
        else:
            tasks.append(idx)

    return tasks
