# type: ignore
__all__ = ["isclose", "_function"]

import random
import time


def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def _function(x):
    """
    Wastes a random amount of time, returns the number 42.01
    """
    time.sleep(random.random() * 4e-4 + 1e-4)
    return 42.01


def _batch_function(batch):
    """
    Wastes a random amount of time, returns the number 42.01 - accepts a batch
    of tasks instead of a single task
    """
    results = []
    for x in batch:
        time.sleep(random.random() * 4e-4 + 1e-4)
        results.append(42.01)
    return results
