# type: ignore
import random

from schwimmbad import JoblibPool, MultiPool, SerialPool
from schwimmbad._test_helpers import _function, isclose


class PoolTestBase:
    all_tasks = [[random.random() for i in range(1000)]]

    def test_init_close(self):
        pool = self.PoolClass()
        pool.close()

    def _make_pool(self):
        return self.PoolClass()

    def test_map(self):
        pool = self._make_pool()

        for tasks in self.all_tasks:
            results = pool.map(_function, tasks)
            count = 0
            for r1, r2 in zip(results, [_function(x) for x in tasks]):
                assert isclose(r1, r2)
                count += 1

            assert count == len(
                tasks
            )  # to make sure iterations through the loop happen!

        pool.close()

    def test_map_callback(self):
        pool = self._make_pool()

        for tasks in self.all_tasks:
            mylist = []

            def _callback(x):
                assert isclose(x, 42.01)
                mylist.append(x)

            results = pool.map(_function, tasks, callback=_callback)
            for r1, r2 in zip(results, [_function(x) for x in tasks]):
                assert isclose(r1, r2)
            assert len(mylist) == len(tasks)

        pool.close()


class TestSerialPool(PoolTestBase):
    def setup_method(self):
        self.PoolClass = SerialPool


class TestMultiPool(PoolTestBase):
    def setup_method(self):
        self.PoolClass = MultiPool


class TestJoblibPool(PoolTestBase):
    def setup_method(self):
        self.PoolClass = JoblibPool
