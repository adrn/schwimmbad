try:
    import numpy as np
    has_numpy = True
except ImportError:
    has_numpy = False

import pytest
from ..utils import batch_tasks


@pytest.mark.skipif(not has_numpy,
                    reason="Numpy is required to run this test")
def test_batch_tasks():
    tasks = batch_tasks(10, n_tasks=100)
    assert len(tasks) == 10
    assert tasks[0] == (0, 10)

    tasks = batch_tasks(10, n_tasks=100, args=(10,))
    assert len(tasks) == 10
    assert tasks[0] == ((0, 10), 10)

    tasks = batch_tasks(10, n_tasks=101, args=(99,))
    assert len(tasks) == 10

    # With array specified
    arr = np.random.random(size=123)
    tasks = batch_tasks(10, arr=arr, args=(99,))
    assert len(tasks) == 10

    arr = np.arange(100)
    tasks = batch_tasks(10, arr=arr, include_idx=False)
    assert np.all(tasks[0] == np.arange(10))

    tasks = batch_tasks(100, n_tasks=5)
    assert len(tasks) == 5

    with pytest.raises(ValueError):
        batch_tasks(0, n_tasks=100)

    with pytest.raises(ValueError):
        batch_tasks(100, n_tasks=0)

    with pytest.raises(ValueError):
        batch_tasks(100, n_tasks=100, arr=arr[:100])
