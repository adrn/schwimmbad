# type: ignore
try:
    import numpy as np

    has_numpy = True
except ImportError:
    has_numpy = False

import pytest

from schwimmbad import choose_pool
from schwimmbad.utils import batch_tasks


@pytest.mark.skipif(not has_numpy, reason="Numpy is required to run this test")
def test_batch_tasks():
    tasks = batch_tasks(10, n_tasks=100)
    assert len(tasks) == 10
    assert tasks[0] == (0, 10)

    tasks = batch_tasks(10, n_tasks=100, args=(10,))
    assert len(tasks) == 10
    assert tasks[0] == ((0, 10), 10)

    tasks = batch_tasks(10, n_tasks=101, args=(99,))
    assert len(tasks) == 10

    # With data specified
    data = np.random.random(size=123)
    tasks = batch_tasks(10, data=data, args=(99,))
    assert len(tasks) == 10

    data = np.arange(100)
    tasks = batch_tasks(10, data=data, include_idx=False)
    assert np.all(tasks[0] == np.arange(10))

    tasks = batch_tasks(100, n_tasks=5)
    assert len(tasks) == 5

    with pytest.raises(ValueError):
        batch_tasks(0, n_tasks=100)

    with pytest.raises(ValueError):
        batch_tasks(100, n_tasks=0)

    with pytest.raises(ValueError):
        batch_tasks(100, n_tasks=100, data=data[:100])


@pytest.mark.parametrize(
    "kwargs", [{"mpi": False, "processes": 1}, {"mpi": False, "processes": 2}]
)
def test_choose_pool(kwargs):
    with choose_pool(**kwargs) as pool:
        pool.map(lambda x: x, range(10))
